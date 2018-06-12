# -*- coding: utf-8 -*-
# author: itimor

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from jsonfield import JSONField
from lbutils import get_or_none
from .config import Process, Node, Transition
from users.models import User
from django.db.models import Q


class ProcessInstance(models.Model):
    PROPERTY_CHOICES = {
        'a': '一般',
        'b': '严重',
        'c': '紧急'
    }
    no = models.CharField('NO.', max_length=100, blank=True)
    name = models.CharField('Title', max_length=255)
    process = models.ForeignKey(Process, on_delete=models.CASCADE)
    property = models.CharField(max_length=1, choices=PROPERTY_CHOICES.items(), default='a', verbose_name=u'问题属性')
    create_user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='instances_create_user')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    create_time = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    cur_node = models.ForeignKey(Node, null=True, on_delete=models.SET_NULL)
    desc = models.TextField('desc', blank=True)

    def __str__(self):
        return self.no

    def create_task(self, operator):
        """ create task for submit/give up/rollback """
        return Task.objects.create(
            instance=self,
            node=self.cur_node,
            user=operator,
        )

    def get_todo_task(self, user=None):
        return self.get_todo_tasks(user).first()

    def get_todo_tasks(self, user=None):
        qs = Task.objects.filter(
            instance=self, node=self.cur_node,
            status='processing').filter(Q(agent_user=user) | Q(user=user))
        if user:
            qs = qs.filter(Q(agent_user=user) | Q(user=user))
        return qs

    def is_user_agreed(self, user):
        events = Event.objects.filter(instance=self).order_by('-create_time', '-id')
        users = []
        for event in events:
            if event.act_type in ['cancel', 'reject', 'back']:
                break
            if event.act_type != 'agree':
                continue
            users.append(event.user)
        return user in users

    def get_operators(self):
        # TODO select_related
        qs = self.task_set.filter(status='in progress')
        users = []
        for e in qs:
            users.extend([e.user, e.agent_user])
        return [e for e in users if e]

    def get_reject_transition(self):
        return self.process.get_reject_transition(self.cur_node)

    def get_back_to_transition(self, out_node=None):
        return self.process.get_back_to_transition(self.cur_node, out_node)

    def get_rollback_transition(self, out_node):
        return self.process.get_rollback_transition(self.cur_node, out_node)

    def get_give_up_transition(self):
        return self.process.get_give_up_transition(self.cur_node)

    def get_transitions(self, only_agree=False, only_can_auto_agree=False):
        qs = Transition.objects.filter(
            process=self.process, input_node=self.cur_node
        ).order_by('is_agree', 'oid', 'id')
        if only_agree:
            qs = qs.filter(is_agree=True)
        if only_can_auto_agree:
            qs = qs.filter(can_auto_agree=True)
        return qs

    def get_agree_transitions(self, only_can_auto_agree=True):
        return self.get_transitions(only_agree=True, only_can_auto_agree=only_can_auto_agree)

    def get_agree_transition(self, only_can_auto_agree=True):
        agree_transitions = self.get_agree_transitions(only_can_auto_agree)
        return agree_transitions[0] if agree_transitions else None

    def last_event(self):
        return self.event_set.order_by('-create_time', '-pk').first()

    def save(self, *args, **kwargs):
        super(ProcessInstance, self).save(*args, **kwargs)
        wf_obj = self.content_object
        if not self.no and wf_obj:  # self.no depend on pk(you should save to get pk)
            self.no = '{}{}'.format(self.process.prefix, self.pk)
            self.create_time = wf_obj.create_time
            self.desc = wf_obj.get_process_summary()
            super(ProcessInstance, self).save(force_update=True)


class Task(models.Model):
    STATUS_CHOICES = {
        'processing': 'processing',
        'completed': 'completed'
    }

    instance = models.ForeignKey(ProcessInstance, on_delete=models.CASCADE)
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    agent_user = models.ForeignKey(User, verbose_name='Agent user', related_name='agent_user_tasks', null=True,
                                   blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES.items(), default='processing')
    receive_time = models.DateTimeField('Receive on', null=True, blank=True)
    is_hold = models.BooleanField('Is hold', default=False)
    create_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {} - {}'.format(self.instance.summary, self.node.name, self.pk)


class Event(models.Model):
    EVENT_ACT_CHOICES = {
        'transition': 'transition',
        'agree': 'agree',
        'edit': 'edit',
        'cancel': 'cancel',
        'reject': 'reject',
        'back': 'back',
        'rollback': 'rollback',
        'comment': 'comment',
        'assign': 'assign',
        'hold': 'hold',
        'unhold': 'unhold',
    }
    instance = models.ForeignKey(ProcessInstance, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    act_type = models.CharField(max_length=255, choices=EVENT_ACT_CHOICES.items(), default='transition')
    act_name = models.CharField(max_length=255, blank=True)
    old_node = models.ForeignKey(Node, related_name='out_events', null=True, blank=True, on_delete=models.CASCADE)
    new_node = models.ForeignKey(Node, related_name='in_events', null=True, blank=True, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, related_name='events', null=True, blank=True, on_delete=models.SET_NULL)
    desc = models.TextField(blank=True, default='')
    ext_data = JSONField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        old_node = self.old_node.name if self.old_node else ''
        new_node = self.new_node.name if self.new_node else ''
        return '{}:{}-{}'.format(self.instance.summary, old_node, new_node)


class BaseWFObj(models.Model):
    pinstance = models.ForeignKey(
        ProcessInstance, blank=True, null=True,
        related_name="%(class)s",
        verbose_name='Process instance',
        on_delete=models.CASCADE
    )
    create_time = models.DateTimeField('Created on', auto_now_add=True)
    create_user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, verbose_name='Created by')

    class Meta:
        abstract = True

    def get_status(self):
        return self.pinstance.cur_node.status

    def get_process_name(self):
        return "%s" % self

    def update_process_summary(self, commit=True):
        pinstance = self.pinstance
        if not pinstance:
            return
        pinstance.name = self.get_process_name()
        if commit:
            pinstance.save()

    def on_complete(self):
        """ Will call when process complete """
        pass

    def on_submit(self):
        """ Will call when process submit """
        pass

    def on_fail(self):
        """ Will call when process fail(cancel/give up/reject)"""
        pass

    def on_do_transition(self, cur_node, to_node):
        """
        Will call when process node transfer
        """
        pass

    def save(self, *args, **kwargs):
        """
        update self.pinstance.summary on save.
        """
        super(BaseWFObj, self).save(*args, **kwargs)
        instance = self.pinstance
        if instance:
            instance.name = self.get_process_name()
            instance.save()

    def create_pinstance(self, process, submit=False):
        """
        Create and set self.pinstance for this model

        :param process: Which process to use
        :param submit: Whether auto submit it after create
        :return: The created process instance
        """
        create_user = self.create_user
        if not isinstance(process, Process):
            process = get_or_none(Process, code=process)
        if not self.pk:
            self.save()
        instance = ProcessInstance.objects.create(
            process=process, create_user=create_user, content_object=self,
            cur_node=process.get_draft_active())
        self.pinstance = instance
        self.save()  # instance will save after self.save
        if submit:
            self.submit_process()
        return instance

    def submit_process(self, user=None):
        """
        Submit this process.

        :param user: Which user submit the process. The user is self.create_user if user is None.
        """
        from workflow.transition import TransitionExecutor

        instance = self.pinstance
        if instance.cur_node.is_submitted():
            return
        user = user or self.create_user
        task = instance.create_task(user)
        transition = instance.get_transitions()[0]
        TransitionExecutor(user, instance, task, transition).execute()


class Issue(BaseWFObj):
    name = models.CharField('Title', max_length=255)
    summary = models.CharField('Summary', max_length=255)
    content = models.TextField('Content', blank=True)

    def __str__(self):
        return self.name
