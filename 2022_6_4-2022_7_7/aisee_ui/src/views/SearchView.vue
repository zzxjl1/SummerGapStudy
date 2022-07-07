<template>
    <div class="frame" @scroll.passive="handleScroll">
        <br>
        <h2>搜索</h2>
        <br>
        <br>
        <div id="search">
            <input v-model="searchfield" type="text" placeholder="在这里键入关键词" />
            <button @click="search()">
                <img src="@/assets/search/search.svg" height="60%" style="display: block;" />
            </button>
        </div>

        <loading :active="isLoading" :can-cancel="false" :is-full-page="false" :opacity="0.5" />

        <br>

        <div class="block">

            <div v-if="!resultShown">
                <div v-if="trending.search.length">
                    <h3>正在热搜</h3>
                    <div class="list no-hairlines trending-search">
                        <ul>

                            <li v-for="(title, index) in trending.search" :key="index" class="item-content">
                                <div class="item-inner">
                                    <div class="item-title"><a class="link" @click="doSearch(title)">{{ title }}</a>
                                    </div>
                                </div>
                            </li>

                        </ul>
                    </div>
                </div>
               
                <div v-else>
                    <h3>大家都在看</h3>
                    <div class="list no-hairlines trending-search">
                        <ul>

                            <li v-for="(title, index) in trending.view" :key="index" class="item-content">
                                <div class="item-inner">
                                    <div class="item-title"><a class="link" @click="doSearch(title)">{{ title }}</a>
                                    </div>
                                </div>
                            </li>

                        </ul>
                    </div>
                </div>
            </div>




            <div class="two-columns-cards">

                <a v-for="news in resultList" :key="news.id" @click="$utils.showNewsDetail(news.id)"
                    v-touch:longtap="longPressHandler(news)">
                    <div class="card">
                        <img v-if="news.bk_img" class="card-image" :src="news.bk_img" />
                        <img v-else class="card-image" src="https://xioyuna.com/envato/yui/demo/Yui/img/thumb-5.jpg" />
                        <div class="card-infos">
                            <h2 class="card-title">{{ news.title }}</h2>
                        </div>
                    </div>
                </a>

            </div>
            
            <div style="height:40px;line-height:40px;font-size: 25px; padding: 20px;">{{ bottomText }}</div>
            <div style="height:80px;hidth:100vw"></div>
        </div>
    </div>
</template>
<script>
import { mapActions } from 'vuex'
import { searchNews, getTrending } from '@/api/index';
import Loading from 'vue-loading-overlay';
import 'vue-loading-overlay/dist/vue-loading.css';
export default {
    components: {
        Loading
    },
    data() {
        return {
            searchfield: "",
            fetchLimit: 20,
            resultList: [],
            isLoading: false,
            bottomText: "",
            debounceTimer: null,
            isEnd: false,
            resultShown: false,
            trending: {
                view: [],
                search: []
            },
        }
    },
    watch: {
        searchfield(val) {
            if (val.length == 0) {
                this.resultShown = false;
                this.resultList = [];
                this.isEnd = false;
                this.bottomText = "";
                this.getTrending();
            }
        }
    },
    methods: {
        ...mapActions(['show_Navbar', 'hide_Navbar']),
        speek(text, preemptive, flush) {
            try {
                // eslint-disable-next-line no-undef
                JS.speek(text, preemptive, flush);
            } catch (e) {
                console.log(e);
            }
        },
        longPressHandler(news) {
            var cxt = this;
            return function () {
                console.log('long press', news);
                cxt.speek(news.title, true, true);
            };
        },
        handleScroll(e) {
            /*
                  //方案1：上下滑动时隐藏导航栏
                  var t = e.target.scrollTop;
                  if (t - this.last_scroll_top < 0) {
                    this.show_Navbar()
                  } else {
                    this.hide_Navbar()
                  }
                  this.last_scroll_top = t;
            */

            //方案2：滑动时隐藏导航栏
            if (e.target.scrollTop > 0) {
                this.hide_Navbar();
                clearInterval(this.navBarHideInterval);
                this.navBarHideInterval = setInterval(() => {
                    this.show_Navbar()
                }, 500)
            }

            if (this.isLoading || this.isEnd || !this.resultShown) return;
            //检测滚动到底部
            if (e.target.scrollTop + e.target.clientHeight >= e.target.scrollHeight) {
                clearTimeout(this.debounceTimer);
                this.bottomText = "正在加载...";
                this.isLoading = true;
                this.debounceTimer = setTimeout(() => {
                    this.fetchMore();
                }, 500);
                console.log("滚动到底部");
            }
        },
        setResultList(data) {
            if (data.length < this.fetchLimit) {
                this.bottomText = "没有更多了";
                this.isEnd = true;
            } else {
                this.bottomText = "";
            }
            this.resultList = data;
        },
        appendResultList(newList) {
            if (newList.length < this.fetchLimit) {
                this.bottomText = "没有更多了";
                this.isEnd = true;
            } else {
                this.bottomText = "";
            }
            var t = this.resultList;
            newList.forEach(element => {
                var id = element.id;
                if (t.findIndex(e => e.id == id) == -1) {
                    t.push(element);
                }
            });
            this.resultList = t;
        },
        search() {
            if (this.searchfield.length == 0) {
                return;
            }
            this.isLoading = true;
            this.bottomText = "正在加载...";
            this.isEnd = false;
            this.resultShown = true;
            var params = new URLSearchParams();
            params.append('payload', this.searchfield);
            params.append('limit', this.fetchLimit);
            searchNews(params).then(res => {
                console.log(res);
                if (res.success) {
                    this.setResultList(res.data);
                } else {
                    this.bottomText = res.description;
                }
            }).finally(() => {
                this.isLoading = false;
            });
        },
        fetchMore() {
            this.isEnd = false;
            var params = new URLSearchParams();
            params.append('payload', this.searchfield);
            params.append('offset', this.resultList.length);
            params.append('limit', this.fetchLimit);
            searchNews(params).then(res => {
                console.log(res);
                if (res.success) {
                    this.appendResultList(res.data);
                } else {
                    this.bottomText = res.description;
                }
            }).finally(() => {
                this.isLoading = false;
            });
        },
        getTrending() {
            getTrending().then(res => {
                console.log(res);
                this.trending = res;
            })
        },
        doSearch(keyword) {
            this.searchfield = keyword;
            this.search();
        },
    },
    mounted() {
        this.getTrending();
    }
}
</script>
<style scoped>
.frame {
    padding-left: 20px;
    padding-right: 20px;
    height: 100vh;
    overflow-x: hidden;
    overflow-y: scroll;
}

h2 {
    padding: 0;
    margin: 0;
    text-align: left;
}

#search {
    width: 100%;
    height: 40px;
    display: flex;
    background-color: rgba(0, 0, 0, 0.05);
    border-radius: 2px;

}

#search input {
    flex: 1;
    height: 100%;
    border: none;
    padding: 0 16px;
    font-size: 13px;
    background: none;
}

#search button {
    padding: 0 32px;
    height: 100%;
    font-size: 22px;
    color: #fff;
    background: #474747;
    border: none;
    cursor: pointer;
}

#search img {
    height: 60%;
}

.block {
    margin: 0;
    padding: 0 5px;
    color: #8A8A8F;
}

.two-columns-cards {
    display: flex;
    flex-flow: row wrap;
    width: 100%;
    margin-bottom: -10px;
}

.two-columns-cards a {
    width: calc(50% - 5px);
    height: 250px;
    margin: 0 0 10px 0;
}

.two-columns-cards .card,
.swiper-container.medium-card-slider .card {
    height: 100%;
    border-radius: 5px;
    /* box-shadow: 0px 5px 35px -10px rgba(0, 0, 0, 0.2); */
}

.two-columns-cards .card-image,
.swiper-container.medium-card-slider .card-image {
    border-radius: 5px;
}

.two-columns-cards a:first-child {
    height: 200px;
    margin-top: 0 !important;
}

.two-columns-cards a:nth-child(2n+1) {
    margin-top: -50px;
    margin-right: 10px;
}

.two-columns-cards a:last-child {
    height: 200px;
}

.two-columns-cards .card-infos,
.swiper-container.medium-card-slider .card-infos {
    padding: 55% 13px 13px 13px;
    border-bottom-left-radius: 5px;
    border-bottom-right-radius: 5px;
}

.two-columns-cards .card-title,
.swiper-container.medium-card-slider .card-title {
    font-size: 18px;
    line-height: 23px;
}

.card {
    position: relative;
    width: 100%;
    height: 400px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    border-radius: 15px;
    cursor: pointer;
    overflow: hidden;
    background: #fff;
    -webkit-transition-duration: 0.3s;
    -moz-transition-duration: 0.3s;
    -o-transition-duration: 0.3s;
    transition-duration: 0.3s;
    -webkit-transition-property: -webkit-transform;
    -moz-transition-property: -moz-transform;
    -o-transition-property: -o-transform;
    transition-property: transform;
}

.card-image {
    object-fit: cover;
    width: 100%;
    height: 100%;
    position: absolute;
    border-radius: 15px;
    border-radius: 5px;
}

.card-infos {
    z-index: 2;
    padding: 20% 20px 20px 20px;
    background-image: linear-gradient(to bottom, rgba(0, 0, 0, 0) 0, rgba(0, 0, 0, 0.8) 100%, rgba(0, 0, 0, 0.9) 100%);
    border-bottom-left-radius: 15px;
    border-bottom-right-radius: 15px;
}

.card-title {
    color: #fff;
    margin: 0;
    font-weight: 700;
    font-size: 18px;
    line-height: 23px;
}

.list ul {
    list-style: none;
    margin: 0;
    padding: 0;
    position: relative;
    background: var(--f7-list-bg-color);
}

.trending-search .item-content {
    padding-left: 0;
    font-size: 22px;
}

.list .item-content {
    display: flex;
    justify-content: space-between;
    box-sizing: border-box;
    align-items: center;
    cursor: pointer;
}

.list .item-title {
    min-width: 0;
    flex-shrink: 1;
    position: relative;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
    padding: 2px 0;
}

.trending-search .item-title a {
    font-size: 21px;
    font-weight: 400;
    color: #ff2d55;
}

.link {
    display: inline-flex;
    align-items: center;
    align-content: center;
    justify-content: center;
    position: relative;
    box-sizing: border-box;
    z-index: 1;
}

.list .item-inner {
    position: relative;
    width: 100%;
    min-width: 0;
    display: flex;
    justify-content: space-between;
    box-sizing: border-box;
    align-items: center;
    align-self: stretch;
    padding-top: 8px;
    padding-bottom: 8px;
    min-height: 44px;
    border-bottom: 1px solid #c1c3c5;
}

</style>