import 'regenerator-runtime/runtime'
import Vue from 'vue'
import App from './App.vue'
import router from './router'
import ViewUI from 'view-design'
import 'view-design/dist/styles/iview.css'
import VueI18n from 'vue-i18n'
import locale from 'view-design/dist/locale/en-US'
import './locale/i18n'
import { validate } from '@/assets/js/validate.js'
import { commonUtil } from '@/pages/util/common-util.js'
import '@/assets/css/local.bootstrap.css'
import 'bootstrap/dist/js/bootstrap.min.js'
import 'font-awesome/css/font-awesome.css'
import jquery from 'jquery'

import DangerousPageTable from '@/pages/components/table-page/page'
import ModalComponent from '@/pages/components/modal'

Vue.prototype.$validate = validate
Vue.prototype.$itsCommonUtil = commonUtil
Vue.prototype.JQ = jquery
Vue.component('DangerousPageTable', DangerousPageTable)
Vue.component('ModalComponent', ModalComponent)

Vue.config.productionTip = false

Vue.use(ViewUI, {
  transfer: true,
  size: 'default',
  VueI18n,
  locale
})

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')
