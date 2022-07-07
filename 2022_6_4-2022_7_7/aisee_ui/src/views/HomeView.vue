<template>
  <div class="home">
  <!--
    <img alt="Vue logo" src="@/assets/logo.png">
    <HelloWorld msg="Welcome to Your Vue.js App" />-->
    <NewsView />
  </div>
</template>

<script>
// @ is an alias to /src
//import HelloWorld from '@/components/HelloWorld.vue'
import NewsView from '@/components/NewsView.vue';

export default {
  name: 'HomeView',
  data() {
    return {
      last_scroll_top: 0,
      navBarHideInterval: null,
    }
  },
  components: {
    //HelloWorld,
    NewsView
},
  methods: {
  },
}
</script>
<style scoped>
.home {
  overflow: scroll;
  height: 100vh;
  padding: 0;
  margin: 0;
}
</style>
