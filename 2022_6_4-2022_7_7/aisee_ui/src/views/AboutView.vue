<template>
  <div class="frame">
    <br>
    <h2>我的</h2>
    <br>
    <br>

    <div v-if="!loginState.logedin" onclick="JS.qqlogin()"
      style="cursor: pointer;text-align:center;width: 25vw;margin: 0 auto;">
      <img style="width:100%" src="@/assets/about/person.svg">
      <span style="display: block;">未登录</span>
    </div>

    <div v-else onclick="JS.logout()" style="cursor: pointer;text-align:center;width: 25vw;margin: 0 auto;">
      <img style="width:100%;border-radius:10%" v-bind:src="get_avatar_url()" />
      <span style="display: block;">{{ loginState.nickname }}</span>
    </div>
    <br><br>


    <div v-if="loginState.logedin" onclick="JS.favorite()" class="wode-item">
      <img src="@/assets/about/personal.svg" />
      <span>我的收藏</span>
      <img style="margin-left:auto;" src="@/assets/about/arrow.svg" />
    </div>
    <!--
    <div class="wode-item">
      <img src="@/assets/about/history.svg" />
      <span>浏览历史</span>
      <img style="margin-left:auto;" src="@/assets/about/arrow.svg" />
    </div>
-->
    <div onclick="JS.settings()" class="wode-item">
      <img src="@/assets/about/settings.svg">
      <span>设置</span>
      <img style="margin-left:auto;" src="@/assets/about/arrow.svg">
    </div>
    <div onclick="JS.aboutus()" class="wode-item">
      <img src="@/assets/about/about.svg">
      <span>关于我们</span>
      <img style="margin-left:auto;" src="@/assets/about/arrow.svg">
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'
export default {
  name: "aboutView",
  data() {
    return {
    }
  },
  computed: {
    loginState: {
      get() {
        return this.$store.state.loginState;
      },
      set(value) {
        this.$store.commit('set_loginState', value);
      }
    },

  },

  methods: {
    ...mapActions(['show_Navbar', 'hide_Navbar']),
    get_avatar_url: function () {
      var base_url = "https://aisee.idealbroker.cn";
      var token = "";
      try {
        // eslint-disable-next-line no-undef
        base_url = JS.get_httpBaseUrl();
        // eslint-disable-next-line no-undef
        token = JS.get_token();
      } catch (e) {
        console.log(e);
      }
      return base_url + "/user/avatar?token=" + token;
    },

  }

}
</script>
<style scoped>
.frame {
  padding-left: 20px;
  padding-right: 20px;
}

h2 {
  padding: 0;
  margin: 0;
  text-align: left;
}

.wode-item {
  cursor: pointer;
  height: 3rem;
  border: 1px solid gray;
  padding: 0 10px 0 10px;
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.wode-item>img {
  height: 60%;
}

.wode-item>span {
  line-height: 3rem;
  font-size: 1.2rem;
  margin-left: 10px;
}
</style>