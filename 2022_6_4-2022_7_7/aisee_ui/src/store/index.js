import { createStore } from "vuex";

export default createStore({
  state: {
    loginState: {
      logedin: false,
      nickname: "",
      id: 0,
    },
    navBarHidden: false,
    micServiceRunning: false,
  },
  getters: {},
  mutations: {
    set_loginState(state, data) {
      state.loginState = data;
    },
    set_navBarHidden(state, val) {
      state.navBarHidden = val;
    },
    set_micServiceRunning(state, val) {
      state.micServiceRunning = val;
    }
  },
  actions: {
    update_loginState(cxt) {
      /* 
      var t = {
        logedin: true,
        nickname: "123",
        id: 0,
      };
      */
      try {
        // eslint-disable-next-line no-undef
        var t = eval("(" + JS.get_loginState() + ")");
        cxt.commit("set_loginState", t);
      } catch {
        console.log("JSbridge not found!");
        return;
      }
    },
    show_Navbar(cxt) {
      cxt.commit("set_navBarHidden", false);
    },
    hide_Navbar(cxt) {
      cxt.commit("set_navBarHidden", true);
    },
    update_micServiceState(cxt) {
      try {
        // eslint-disable-next-line no-undef
        var t = eval("(" + JS.get_micServiceState() + ")");
        cxt.commit("set_micServiceRunning", t);
      } catch {
        console.log("JSbridge not found!");
        return;
      }
    }
  },
  modules: {},
});
