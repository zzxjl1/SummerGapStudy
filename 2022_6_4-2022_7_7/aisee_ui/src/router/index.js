import { createRouter, createWebHashHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import AboutView from "../views/AboutView.vue";
import ToolBoxView from "../views/ToolBoxView.vue";
import SearchView from "../views/SearchView.vue";
const routes = [
  {
    path: "/",
    name: "新闻",
    component: HomeView,
  },
  {
    path: "/about",
    name: "我的",
    component: AboutView,
  },
  {
    path: "/toolbox",
    name: "工具箱",
    component: ToolBoxView,
  },
  {
    path: "/search",
    name: "搜索",
    component: SearchView,
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

var first_launch = true;
// eslint-disable-next-line no-unused-vars
router.afterEach((to, from) => {
  console.log(to.name);
  if (!first_launch) {
    // eslint-disable-next-line no-undef
    JS.speek(to.name, true, true);
  }
  first_launch = false;
});
export default router;
