<template>
  <nav id="nav" :class="{ hidden: isHidden }">

    <router-link to="/" class="tab-item">
      <div class="tab-frame">
        <img src="@/assets/nav_bar/notebook.svg">
        <span>新闻</span>
      </div>
    </router-link>

    <router-link to="/search" class="tab-item">
      <div class="tab-frame">
        <img src="@/assets/nav_bar/search.svg">
        <span>搜索</span>
      </div>
    </router-link>

    <a class="tab-item">
      <div class="tab-frame" :class="{ changecolor: micServiceRunning }" onclick="JS.toggle_micService()">
        <img style="width:45px;padding:0;" src="@/assets/nav_bar/mic.png">
        <span>语音控制</span>
      </div>
    </a>

    <router-link to="/toolbox" class="tab-item">
      <div class="tab-frame">
        <img src="@/assets/nav_bar/web.svg">
        <span>工具箱</span>
      </div>
    </router-link>

    <router-link to="/about" class="tab-item">
      <div class="tab-frame">
        <img src="@/assets/nav_bar/person.svg">
        <span>我的</span>
      </div>
    </router-link>

  </nav>
  <router-view v-slot="{ Component }">
    <keep-alive>
      <component :is="Component" />
    </keep-alive>
  </router-view>
</template>
<script>
import { mapActions } from 'vuex';
import { ping } from '@/api/index';

export default {
  name: "navBar",
  data() {
    return {
    }
  },
  computed: {
    isHidden: {
      get() {
        return this.$store.state.navBarHidden;
      }
    },
    micServiceRunning: {
      get() {
        return this.$store.state.micServiceRunning;
      }
    }
  },
  methods: {
    ...mapActions(['update_loginState','update_micServiceState']),
    startcapture() {
      // eslint-disable-next-line no-undef
      JS.startcapture();
    }
  },
  mounted() {
    //onCreated
    this.update_loginState();
    this.update_micServiceState();
    ping().then(res => {
      console.log(res);
    }).catch((err) => {
      console.log(err);
    });
  },
}
</script>


<style>
* {
  /*-webkit-tap-highlight-color: red;*/
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  -khtml-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

body {
  height: 100vh;
  padding: 0;
  margin: 0;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

a,
a:hover,
a:active {

  color: #000;
  text-decoration: none;
}

nav {
  border-radius: 10px;
  box-shadow: 0px 2px 10px 0px #333;
  position: fixed;
  width: 94vw;
  height: 70px;
  bottom: 10px;
  left: 3vw;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(5px);
  z-index: 999;
  white-space: nowrap;
  display: flex;
  font-size: 0;
  transition: transform .5s;
  z-index: 2147483647;
}

.hidden {
  transform: translateY(80px);
}


.tab-item {
  cursor: pointer;
  height: 100%;
  width: 20%;
  text-align: center;
  font-size: 10px;
}

.tab-frame {
  margin: 5px;
  padding: 0px;
  text-align: center;
  vertical-align: middle;
  height: calc(100% - 10px);

}

.tab-frame>img {
  width: 35px;
  padding: 5px;
  display: block;
  margin: 0 auto;
}

.tab-frame>span {
  font-size: 10px;
  line-height: 10px;
}

.changecolor {
  border-radius: 5%;
  background: #47a3da;
  -webkit-animation-duration: 5000ms;
  -webkit-animation-iteration-count: infinite;
  -webkit-animation-timing-function: linear;
  -webkit-animation-name: 'GrowQuare';

}

@-webkit-keyframes GrowQuare {
  50% {
    background: #99CC00;
    border-radius: 20%;
  }
}

.router-link-active {
  background: #ffeb3bc4;
    border-radius: 8px;
}
</style>
