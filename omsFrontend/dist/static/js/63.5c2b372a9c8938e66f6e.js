webpackJsonp([63],{z8an:function(e,t,i){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var n={data:function(){return{checkAll:!1,checkedCities:[],cities:["上海","北京","广州","深圳"],isIndeterminate:!0}},methods:{handleCheckAllChange:function(e){this.checkedCities=e?this.cities:[],this.isIndeterminate=!1},handleCheckedCitiesChange:function(e){var t=e.length;this.checkAll=t===this.cities.length,this.isIndeterminate=t>0&&t<this.cities.length}}},c=function(){var e=this,t=e.$createElement,i=e._self._c||t;return i("div",[i("el-checkbox",{attrs:{indeterminate:e.isIndeterminate},on:{change:e.handleCheckAllChange},model:{value:e.checkAll,callback:function(t){e.checkAll=t},expression:"checkAll"}},[e._v("全选")]),e._v(" "),i("div",{staticStyle:{margin:"15px 0"}}),e._v(" "),i("el-checkbox-group",{on:{change:e.handleCheckedCitiesChange},model:{value:e.checkedCities,callback:function(t){e.checkedCities=t},expression:"checkedCities"}},e._l(e.cities,function(t){return i("el-checkbox",{key:t,attrs:{label:t}},[e._v(e._s(t))])}))],1)},l=[],s={render:c,staticRenderFns:l},h=s,a=i("VU/8"),r=a(n,h,!1,null,null,null);t.default=r.exports}});