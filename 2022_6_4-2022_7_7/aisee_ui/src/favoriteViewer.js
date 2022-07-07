import { createApp } from "vue";
import App from "./FavoriteViewer.vue";
import utils from "@/plugins/utils";
import VueSweetalert2 from 'vue-sweetalert2';
import 'sweetalert2/dist/sweetalert2.min.css';

const app = createApp(App);
app.config.globalProperties.$utils = utils;
app.use(VueSweetalert2).mount("#app");
