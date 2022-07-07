import { createApp } from "vue";
import App from "./OCRViewer.vue";
import utils from "@/plugins/utils";

const app = createApp(App);
app.config.globalProperties.$utils = utils;
app.mount("#app");
