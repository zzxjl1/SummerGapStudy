<template>
    <swiper id="tab" class="tab" :slides-per-view="5" :free-mode="true" @beforeInit="barInit" :modules="modules">
        <swiper-slide v-for="(name, index) in tabItems" :key="index" class="tabItem"
            :class="{ active: index == selectedTabIndex }" @click="onTabClick(index)">{{ name }}</swiper-slide>
    </swiper>

    <swiper :slides-per-view="1" :spaceBetween="0" @slideChange="onTabSlideChange" @sliderMove="onScroll"
        @beforeInit="tabInit" :modules="modules">
        <loading :active="isLoading" :can-cancel="false" :is-full-page="false" :opacity="0.5" />
        <div v-if="isError" class="loading-overlay" @click="fetchNews"><span style="width:100%">加载失败</span></div>
        <swiper-slide v-for="(name, index) in tabItems" :key="index" class="container">
            <swiper class="swiper-fix" :slides-per-view="2.5" :direction="'vertical'" :spaceBetween="0"
                :auto-height="true" :scrollbar="{ hide: true }" @slideChange="onNewsSlideChange" @sliderMove="onScroll"
                @touch-move="pullHandler" @touch-end="refreshHandler"
                :modules="modules">
                <div class="pull-to-refresh">{{ pullToRefreshText }}</div>
                <swiper-slide v-for="(news, index) in newsArray[name]['data']" :key="index">
                    <NewsItem :title="news.title" :tags="news.tags" :created_at="news.created_at" :source="news.source"
                        :bk_img="news.background_img" :click_count="news.click_count" :like_count="news.like_count"
                        :comment_count="news.comment_count" @click="$utils.showNewsDetail(news.id)"
                        v-touch:longtap="longPressHandler(news.title)" />
                </swiper-slide>
                <swiper-slide v-if="newsArray[name]['isEnd']" style="background:wheat">到底了</swiper-slide>
            </swiper>
        </swiper-slide>

    </swiper>
</template>
<script>
import { getCurrentInstance, ref } from 'vue';
import { mapActions } from 'vuex'
import { getNewsByCategory } from '@/api/index';
import { Swiper, SwiperSlide } from "swiper/vue";
import { Scrollbar, FreeMode } from "swiper";
import NewsItem from '@/components/NewsItem.vue';
import "swiper/css";
import "@/assets/home/iconfont.css";
import "swiper/css/scrollbar";
import Loading from 'vue-loading-overlay';
import 'vue-loading-overlay/dist/vue-loading.css';
var cxt;
var bar;
var tab;
// eslint-disable-next-line no-unused-vars
var newsSwiper={};
export default ({
    name: 'newsView',
    components: {
        Swiper,
        SwiperSlide,
        NewsItem,
        Loading,
    },
    setup() {
        var navBarHideTimeout = ref({});
        //var newsBroadcastTimeout = ref({});
        const _instance = getCurrentInstance();
        const { $store } = _instance.appContext.app.config.globalProperties;
        const onNewsSlideChange = (swiper) => {
            console.log('news slide change', swiper);
            var index = swiper.activeIndex;
            newsSwiper[cxt.selectedTabIndex] = swiper;
            console.log('newsSwiper', newsSwiper);
            /*
            clearTimeout(newsBroadcastTimeout);
            newsBroadcastTimeout = setTimeout(() => {
                var text = cxt.getNewsList(cxt.selectedTabIndex)[index].title;
                cxt.speek(text, true, true);
            }, 1500);
            */
            if (index + 5 > swiper.slides.length) {
                cxt.fetchMore();
            }
        };
        const onTabSlideChange = (swiper) => {
            console.log('tab slide change', swiper);
            cxt.selectedTabIndex = swiper.activeIndex;
        };
        const onScroll = () => {
            $store.dispatch("hide_Navbar");
            clearTimeout(navBarHideTimeout);
            navBarHideTimeout = setTimeout(() => {
                $store.dispatch("show_Navbar");
            }, 500);
        };
        const barInit = (swiper) => {
            //console.log('bar init', swiper);
            bar = swiper;
        };
        const tabInit = (swiper) => {
            //console.log('tab init', swiper);
            tab = swiper;
        };
        var last = '';
        const pullHandler = (swiper) => {
            if (!swiper.isBeginning || swiper.translate <= 0) {
                cxt.pullToRefreshText = '';
                return;
            }

            last = cxt.pullToRefreshText;
            if (swiper.translate < 70 && swiper.translate > 20) {
                cxt.pullToRefreshText = '继续下拉';
            } else if (swiper.translate > 70) {
                cxt.pullToRefreshText = '松开刷新';
            }

            if (last != cxt.pullToRefreshText) {
                cxt.speek(cxt.pullToRefreshText, true, true);
            }
        };
        const refreshHandler = (swiper) => {
            if (swiper.translate > 70) {
                cxt.fetchNews();
                cxt.speek("刷新", true, true);
            }
        };
        return {
            modules: [Scrollbar, FreeMode],
            onNewsSlideChange,
            onTabSlideChange,
            onScroll,
            barInit,
            tabInit,
            pullHandler,
            refreshHandler,
        };
    },
    data() {
        var tabItems = ["推荐", "最新", "科技", "社会", "数码", "财经", "娱乐", "教育", "体育", "军事", "历史"];
        var newsArray = {};
        tabItems.forEach(e => {
            newsArray[e] = {
                "data": [],
                "isEnd": false,
            };
        });
        return {
            tabItems: tabItems,
            selectedTabIndex: 0,
            newsArray: newsArray,
            navBarHideTimeout: null,
            pullToRefreshText: '',
            isLoading: false,
            isError: false,
            fetchLimit: 5,
            newsBroadcastTimeout: null,
        }
    },
    methods: {
        ...mapActions(['show_Navbar', 'hide_Navbar']),

        speek(text, preemptive, flush) {
            try {
                // eslint-disable-next-line no-undef
                JS.speek(text, preemptive, flush);
            } catch (e) {
                console.log(text);
            }
        }, 
        longPressHandler(t) {
            var cxt = this;
            return function () {
                console.log('long press', t);
                cxt.speek(t, true, true);
            };
        },
        getTabName(index, lang = "zh") {
            if (lang == "zh") {
                return this.tabItems[index];
            } else if (lang == "en") {
                return this.tabItemsEN[index];
            }

        },
        getNewsList(index) {
            return this.newsArray[this.getTabName(index)]["data"];
        },
        setNewsList(index, newsList) {
            this.newsArray[this.getTabName(index)]["data"] = newsList;
        },
        appendNewsList(index, newsList) {
            var t = this.newsArray[this.getTabName(index)]["data"];
            newsList.forEach(element => {
                var id = element.id;
                if (t.findIndex(e => e.id == id) == -1) {
                    t.push(element);
                }
            });
            this.newsArray[this.getTabName(index)]["data"] = t;
        },
        fetchNews() {
            this.isLoading = true;
            var params = new URLSearchParams();
            var type = this.getTabName(this.selectedTabIndex);
            params.append('limit', this.fetchLimit);
            getNewsByCategory(type, params).then(res => {
                console.log(res);
                this.setNewsList(this.selectedTabIndex, res);
                this.isError = false;
                //cxt.speek("加载成功", true, true);
            }).catch((err) => {
                this.isError = true;
                console.log(err);
                cxt.speek("加载失败，点按刷新", true, true);
            }).finally(() => {
                this.isLoading = false;
            });
        },
        fetchMore() {
            var length = this.getNewsList(this.selectedTabIndex).length;
            var params = new URLSearchParams();
            var type = this.getTabName(this.selectedTabIndex);
            if (length > 0) {
                var offset = this.getNewsList(this.selectedTabIndex)[length - 1].created_at;
                params.append('offset', offset);
            }
            params.append('limit', this.fetchLimit);
            getNewsByCategory(type, params).then(res => {
                console.log(res);
                if (res.length < this.fetchLimit) {
                    this.newsArray[this.getTabName(this.selectedTabIndex)]["isEnd"] = true;
                }
                this.appendNewsList(this.selectedTabIndex, res);
            }).catch((err) => {
                console.log(err);
            }).finally(() => {
            });
        },
        onTabClick(index) {
            console.log(index);
            if (index == this.selectedTabIndex) {
                newsSwiper[index].slideTo(0);
                return;
            }
            this.selectedTabIndex = index
        },
    },
    mounted() {
        cxt = this;
        this.fetchNews();
    },
    watch: {
        selectedTabIndex(val) {
            bar.slideTo(val);
            tab.slideTo(val);
            if (this.getNewsList(val).length == 0) {
                this.fetchNews();
            }
            this.speek(this.getTabName(val), true, true);
        }
    }
});
</script>
<style scoped>
.swiper {
    position: fixed;
    top: 20px;
    bottom: 0px;
    width: 100vw;
}

.swiper-slide {
    text-align: center;
    font-size: 50px;
    color: yellowgreen;
    /*background: yellow;*/
    display: flex;
    justify-content: center;
    align-items: center;
}

.container {
    background: whitesmoke;
    height: 100vh;
    width: 100vw;
}

.pull-to-refresh {
    position: absolute;
    width: 100%;
    top: 15px;
    font-size: 20px;
    align-items: center;
}

.tab {
    width: 100%;
    height: 40px;
    overflow: hidden;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 999;
    background: white;
}

.tabItem {
    width: 20%;
    height: 40px;
    float: left;
    background: white;
    line-height: 40px;
    text-align: center;
    font-size: 20px;
}

.active {
    height: 40px;
    border-bottom: 3px solid #FE2D26;
    box-sizing: border-box;
}

.loading-overlay {
    position: fixed;
    display: flex;
    align-items: center;
    font-size: 50px;
    color: aqua;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 999;
}
</style>