webpackJsonp([102],{u0UT:function(t,a,e){"use strict";Object.defineProperty(a,"__esModule",{value:!0});var s={components:{},props:["Status","statusdata"],data:function(){return{}},created:function(){},methods:{submitForm:function(t){this.$emit("formdata",this.statusdata)}}},u=function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("el-form",[e("el-form-item",{attrs:{model:t.statusdata,label:"当前状态"}},[e("span",[t._v(t._s(t.Status[t.statusdata.status]))])]),t._v(" "),e("el-form-item",{attrs:{model:t.statusdata,label:"状态修改"}},[e("el-select",{attrs:{placeholder:"请选择状态"},model:{value:t.statusdata.status,callback:function(a){t.$set(t.statusdata,"status",a)},expression:"statusdata.status"}},t._l(t.Status,function(t,a){return e("el-option",{key:t.id,attrs:{label:t,value:a}})}))],1),t._v(" "),e("el-form-item",[e("el-button",{attrs:{type:"primary",icon:"el-icon-check"},on:{click:t.submitForm}},[t._v("提交")])],1)],1)},l=[],n={render:u,staticRenderFns:l},r=n,o=e("VU/8"),i=o(s,r,!1,null,null,null);a.default=i.exports}});