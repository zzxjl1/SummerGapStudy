/* eslint-disable no-unused-vars */
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import timeago from 'vue-timeago3'
import { zhCN } from 'date-fns/locale'
import VueSweetalert2 from 'vue-sweetalert2';
import 'sweetalert2/dist/sweetalert2.min.css';
import Vue3TouchEvents from "vue3-touch-events";
import utils from "@/plugins/utils"

const timeagoOptions = {
    converterOptions: {
        includeSeconds: false,
    },
    locale: zhCN,
  }

const app = createApp(App);
app.config.globalProperties.$utils = utils
app.use(store).use(router).use(timeago,timeagoOptions).use(VueSweetalert2).use(Vue3TouchEvents).mount("#app");

