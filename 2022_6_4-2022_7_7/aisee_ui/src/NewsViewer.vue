<template>

    <div class="page single" @scroll.passive="onScroll">

        <div v-if="news">
            <img :src="news.background_img ? news.background_img : 'https://mdbcdn.b-cdn.net/img/new/fluid/city/018.webp'"
                id="bk-img">
            <div class="img-bottom-banner">
                <div>
                    <i class="iconfont icon-star fab" :class="{ on: news.favorited }" @click="toggle_favorite()"></i>
                </div>
                <div>
                    <i class="iconfont icon-like fab" :class="{ on: news.liked }" style="font-size:25px"
                        @click="toggle_like()"></i>
                </div>
            </div>
            <div class="block article" style="min-height: 100vh;">
                <div class="post-infos">
                    <div class="post-category" id="category">{{ news.category }}</div>
                    <div class="post-date">
                        <timeago :datetime="news.created_at" id="created_at" />
                    </div>
                </div>
                <h1 id="title">{{ news.title }}</h1>
                <blockquote class="blockquote">
                    <div class="summary">
                        <span v-for="(item, index) in news.summary.splited" :key="index" :id="item.id">{{ item.text
                        }}</span>
                    </div>
                    <span id="source">来源于 {{ news.source }}</span>
                </blockquote>

                <div v-for="(i, index) in news.content" :key="index">
                    <p v-if="i.type == 'paragraph'">
                        <span v-for="(item, item_index) in i.splited" :key="item_index" :id="item.id">
                            {{ item.text }}
                        </span>
                    </p>
                    <p v-if="i.type == 'title'" :id="i.id"><strong>{{ i.text }}</strong></p>
                    <img v-if="i.type == 'img'" :src="i.url" :id="i.id" />
                    <div v-if="i.type == 'img_with_caption'" class="image-with-text" :id="i.id">
                        <img :src="i.url" :id="i.id + '_img'">
                        <div class="image-text" :id="i.id + '_text'"><i>{{ i.caption }}</i></div>
                    </div>
                </div>
            </div>

            <div class="block" id="artical-end">

                <div v-if="related_news_list.length != 0" class="title-medium-container">
                    <h2>相关新闻</h2>
                </div>

                <swiper :slides-per-view="1.3" :space-between="10">
                    <swiper-slide v-for="news in related_news_list" :key="news.id"
                        @click="$utils.showNewsDetail(news.id)">
                        <div class="card">
                            <img v-if="news.bk_img" class="card-image" :src="news.bk_img">
                            <img v-else class="card-image"
                                src="https://xioyuna.com/envato/yui/demo/Yui/img/thumb-5.jpg" />

                            <div class="card-infos">
                                <h2 class="card-title">{{ news.title }}</h2>
                            </div>
                        </div>
                    </swiper-slide>
                </swiper>
            </div>



            <div class="block">
                <div class="title-medium-container" style="align-items: center;display: flex;">
                    <h2 style="display: inline-flex;">评论</h2>
                    <a class="big-button twitter link" @click="reply_to_news()"
                        style="width: 100px;height: 35px;right: 0;position: absolute;">发表评论</a>
                </div>

                <swiper :effect="'cards'" :grabCursor="true" @slideChange="onCommentSlideChange" :modules="modules"
                    class="commentSwiper">
                    <template v-if="showCommentCover">
                        <swiper-slide>{{ commentCoverText }}</swiper-slide>
                        <swiper-slide v-if="commentCoverText == `暂无评论`">试试发表一个~</swiper-slide>
                    </template>>
                    <swiper-slide v-for="comment in commentList" :key="'comment_' + comment.id">

                        <div class="comment">
                            <div class="author-block">
                                <img :src="get_avatar_url(comment.user.avatar)" alt="">
                                <div class="author-infos">
                                    <div class="author-name">{{ comment.user.nickname }}</div>
                                    <div class="author-description">
                                        IP属地：{{ comment.geo_location }}<br>
                                        <timeago :datetime="comment.created_at" :id="'timeago_' + comment.id" />
                                    </div>
                                </div>
                            </div>
                            <div class="content">
                                {{ comment.content }}
                            </div>
                            <div class="foot-banner">
                                <div @click="comment_like(comment)" class="foot-banner-item"
                                    :class="{ almostTransparent: !comment.liked }">
                                    <img src="@/assets/viewer/like.svg" />
                                    <span>{{ comment.like_count }}</span>
                                </div>
                                <div class="foot-banner-item" @click="broadcastComment(comment)">
                                    <img src="@/assets/viewer/speaker.svg" />
                                    <span>朗读</span>
                                </div>
                                <div @click="comment_dislike(comment)" class="foot-banner-item"
                                    :class="{ almostTransparent: !comment.disliked }"><img
                                        src="@/assets/viewer/dislike.svg" />
                                    <span>{{ comment.dislike_count }}</span>
                                </div>
                            </div>
                        </div>

                    </swiper-slide>
                    <swiper-slide v-if="!showCommentCover">到底了</swiper-slide>

                </swiper>
            </div>


        </div>

        <loading :active="!news" :can-cancel="false" :is-full-page="true" :opacity="1" />

        <div class="sub-box" :class="{ show: scroll_top_btn_visible || news_broadcast_interval }">
            <div @click="scrollToTop()">
                <i class="iconfont icon-top fab fab-large"></i>
            </div>

            <div @click="toggleNewsBroadcast()">
                <i class="iconfont icon-speak fab fab-large" :class="{ on: news_broadcast_interval }"></i>
            </div>
        </div>


        <div class="control-pannel" v-if="news_broadcast_interval">

            <a class="btn" @click="backwardNewsBroadcast()">
                <i class="iconfont icon-backward"></i>
            </a>
            <a class="btn" @click="playPauseNewsBroadcast()">
                <i v-if="news_broadcast_paused" class="iconfont icon-play"></i>
                <i v-else class="iconfont icon-pause"></i>
            </a>
            <a class="btn" @click="forwardNewsBroadcast()">
                <i class="iconfont icon-forward"></i>
            </a>

        </div>

    </div>



</template>

<script>
import { getDetailedNews, postComment, getComment, performCommentOperation, toggleFavorite, toggleLike, relatedNews } from '@/api/index';
import { Swiper, SwiperSlide } from 'swiper/vue';
import { EffectCards } from "swiper";
import 'swiper/css';
import "swiper/css/effect-cards";
import Loading from 'vue-loading-overlay';
import 'vue-loading-overlay/dist/vue-loading.css';
import queue from '@/plugins/queue';
import { Howl } from 'howler';
import "@/assets/home/iconfont.css";
var cxt;
export default ({
    data() {
        return {
            newsId: null,
            news: null,
            isLoading: true,
            ws: null,
            commentsVisible: true,
            commentList: [],
            fetchLimit: 5,
            showCommentCover: true,
            commentCoverText: '',
            newsBroadcastQueue: queue,
            tts_preload_threshold: 2,
            news_broadcast_interval: null,
            news_broadcast_paused: false,
            isPlaying: false,
            scroll_top_btn_visible: false,
            related_news_list: [],
        }
    },
    computed: {

    },
    components: {
        Swiper,
        SwiperSlide,
        Loading,
    },
    setup() {

        const onCommentSlideChange = (swiper) => {
            var index = swiper.activeIndex;
            if (index + 5 > swiper.slides.length) {
                cxt.fetchMoreComment();
            }
        };
        return {
            modules: [EffectCards],
            onCommentSlideChange,
        };
    },
    methods: {
        scrollToTop() {
            document.getElementById("bk-img")?.scrollIntoView({
                behavior: "smooth",
            });
            this.speek("滚动到顶部", true, true);
        },
        onScroll(e) {
            var scrollTop = e.target.scrollTop;
            var clientHeight = e.target.clientHeight;
            //console.log(scrollTop,clientHeight);
            if (scrollTop > document.getElementById('bk-img').scrollHeight + 0 &&
                scrollTop + clientHeight < document.getElementById('artical-end').offsetTop) {
                this.scroll_top_btn_visible = true;
            } else {
                this.scroll_top_btn_visible = false;
            }

        },
        splitParagraph(text) {
            var result = [];
            var temp = '';
            for (var i = 0; i < text.length; i++) {
                if (text[i] == '。' /*|| text[i] == '，' || text[i] == '；' || text[i] == '？' || text[i] == '！' */) {
                    result.push({ type: 'sub_sentence', text: temp });
                    result.push({ type: 'punctuation', text: text[i] });
                    temp = '';
                } else {
                    temp += text[i];
                }
            }
            if (temp != '') { result.push({ type: 'sub_sentence', text: temp }); }

            return result;
        },
        parseNews() {
            var text = this.news.summary;
            var splited = this.splitParagraph(text);
            splited.forEach((item, index) => {
                item["id"] = `data_summary_${index}`;
            });
            this.news.summary = {
                text: text,
                splited: splited
            }
            this.news.content.forEach((item, index) => {
                var prefix = "data_content"
                switch (item.type) {
                    /*
                    case 'title':
                        item["id"] = `${prefix}_${index}`;
                        break;
                    */
                    case 'paragraph':
                        var splited = this.splitParagraph(item.text, index);
                        splited.forEach((item, index2) => {
                            item["id"] = `data_content_${index}_${index2}`;
                        });
                        item["splited"] = splited;
                        break;
                    default:
                        item["id"] = `${prefix}_${index}`;
                        break;
                }
            });
        },
        speek(text, preemptive, flush) {
            try {
                // eslint-disable-next-line no-undef
                JS.speek(text, preemptive, flush);
            } catch (e) {
                console.log(e);
            }
        },
        toast(t) {
            try {
                // eslint-disable-next-line no-undef
                JS.toast(t);
            } catch (e) {
                console.log(t);
            }
        },
        getQueryVariable(variable) {
            var query = window.location.search.substring(1);
            var vars = query.split("&");
            for (var i = 0; i < vars.length; i++) {
                var pair = vars[i].split("=");
                if (pair[0] == variable) { return pair[1]; }
            }
            return;
        },
        getNewsId() {
            var t = 1;
            try {
                // eslint-disable-next-line no-undef
                t = JS.getNewsId();
            } catch (e) {
                t = this.getQueryVariable("id");
            }
            return t;
        },
        getNews() {
            var params = new URLSearchParams();
            params.append('id', this.newsId);
            params.append('token', this.get_token());
            var description = '';
            getDetailedNews(params).then(res => {
                console.log(res);
                if (res.success) {
                    this.news = res.result;
                    this.parseNews();
                    console.log(this.news);
                    this.fetch_related_news();
                } else {
                    description = res.description;
                }
            }).catch(err => {
                console.log(err);
                description = err.message;
            }).finally(() => {
                this.isLoading = false;
                if (description) {
                    this.$swal({
                        title: '请求失败',
                        text: description,
                        icon: 'error',
                        confirmButtonText: '返回',
                        allowOutsideClick: false,
                    }).then((result) => {
                        console.log(result);
                        // eslint-disable-next-line no-undef
                        JS.exit();
                    });
                }
            });
        },
        appendCommentList(commentList) {
            var t = this.commentList;
            commentList.forEach(element => {
                var id = element.id;
                if (t.findIndex(e => e.id == id) == -1) {
                    t.push(element);
                }
            });
            this.commentList = t;
        },
        fetchComment() {
            this.showCommentCover = true;
            this.commentCoverText = "评论加载中...";
            var params = new URLSearchParams();
            params.append('news_id', this.newsId);
            params.append('limit', this.fetchLimit);
            params.append('token', cxt.get_token());
            getComment(params).then(res => {
                console.log(res);
                if (res.success) {
                    this.commentList = res.result;
                    if (res.result.length == 0) {
                        this.commentCoverText = "暂无评论";
                    } else {
                        this.showCommentCover = false;
                    }
                } else {
                    this.commentCoverText = res.description;
                }
            }).catch(err => {
                this.commentCoverText = "评论载入失败:" + err;
                console.log(err);
            });
        },
        fetchMoreComment() {
            var length = this.commentList.length;
            var params = new URLSearchParams();
            if (length > 0) {
                var offset = this.commentList[length - 1].created_at;
                params.append('offset', offset);
            }
            params.append('news_id', this.newsId);
            params.append('limit', this.fetchLimit);
            params.append('token', cxt.get_token());
            getComment(params).then(res => {
                console.log(res);
                if (res.result.length < this.fetchLimit) {
                    console.log("it's the end");
                }
                this.appendCommentList(res.result);
            }).catch((err) => {
                console.log(err);
            });
        },
        get_ws_base_url() {
            var ws_base_url;
            try {
                // eslint-disable-next-line no-undef
                ws_base_url = JS.get_wsBaseUrl();
            } catch (e) {
                ws_base_url = "ws://192.168.31.114:4000";
            }
            return ws_base_url;
        },
        get_http_base_url() {
            var http_base_url;
            try {
                // eslint-disable-next-line no-undef
                http_base_url = JS.get_httpBaseUrl();
            } catch (e) {
                http_base_url = "http://192.168.31.114:4000";
            }
            return http_base_url;
        },
        get_avatar_url(t) {
            return `${this.get_http_base_url()}/user/avatar/${t}`;
        },
        get_token() {
            var token;
            try {
                // eslint-disable-next-line no-undef
                token = JS.get_token();
            } catch (e) {
                token = "KpMP6U1nySvocbAWdtx4qhTZgHmFuVRi";
            }
            return token;
        },
        open_ws_connection() {
            var ws_base_url = this.get_ws_base_url();
            var heartbeat_interval = 1000 * 10;
            var cxt = this;
            this.ws = new WebSocket(`${ws_base_url}/view_history/${this.newsId}`);
            this.ws.onopen = function () {
                console.log('ws connection open');
                cxt.ws.send(cxt.get_token());
                heartbeat_interval = setInterval(function () {
                    cxt.ws.send(JSON.stringify({ action: 'heartbeat' }));
                }, heartbeat_interval);
            };
            this.ws.onmessage = function (event) {
                console.log(event.data);
            };
            this.ws.onclose = function () {
                console.log('ws connection close');
                clearInterval(heartbeat_interval);
            };
            this.ws.onerror = function () {
                console.log('ws connection error');
                setTimeout(function () {
                    cxt.open_ws_connection();//reconnect
                }, 1000);
            };
        },
        reply_to_news() {
            try {
                // eslint-disable-next-line no-undef
                JS.reply_to_news();
            } catch (e) {
                var text = prompt("发表评论", "请在此输入内容");
                this.send_reply_to_news(text);
            }
        },
        send_reply_to_news(text) {

            console.log(text);
            var cxt = this;
            var params = new URLSearchParams();
            params.append('content', text);
            params.append('target_id', cxt.newsId);
            params.append('is_reply', false);
            params.append('token', cxt.get_token());
            postComment(params).then(res => {
                cxt.toast(res.description);
                if (res.success) {
                    setTimeout(function () {
                        cxt.fetchComment();
                    }, 1000);
                }
            }).catch(err => {
                console.log(err);
            });

        },
        update_like_dislike_count(comment, operation) {
            var params = new URLSearchParams();
            params.append('comment_id', comment.id);
            params.append('operation', operation);
            params.append('token', cxt.get_token());
            performCommentOperation(params).then(res => {
                this.toast(res.description);
                if (res.success) {
                    switch (operation) {
                        case 'like':
                            comment.liked = !comment.liked;
                            comment.like_count = res.new_val;
                            break
                        case 'dislike':
                            comment.disliked = !comment.disliked;
                            comment.dislike_count = res.new_val;
                            break
                    }
                }
            }).catch(err => {
                console.log(err);
            });
        },
        comment_like(comment) {
            this.update_like_dislike_count(comment, 'like');
        },
        comment_dislike(comment) {
            this.update_like_dislike_count(comment, 'dislike');
        },
        broadcastComment(comment) {
            var timeago = document.getElementById(`timeago_${comment.id}`).innerText;
            var text = `${comment.geo_location} 网友 ${comment.user.nickname} ${timeago} 评论如下 ${comment.content} 收获了${comment.like_count}个赞和${comment.dislike_count}个踩`;
            console.log(text);
            this.speek(text, true, true);
        },
        broadcast() {
            if (this.news_broadcast_paused) return;

            var item = this.newsBroadcastQueue.front();

            if (item.sound.state() == "unloaded" && !item.sound._preload) {
                item.sound.load();
                item.start_load_timestamp = new Date();
                return;
            }
            if (item.sound.state() == "loading") {
                console.log("wav file is still loading...");
                //TIME DIFFERENCE IN SECONDS
                var timeDiff = (new Date() - item.start_load_timestamp) / 1000;
                if (timeDiff > 10) {
                    var t = cxt.newsBroadcastQueue.dequeue();
                    console.log("wav file loading timeout", t);
                    cxt.speek("发生了读取错误", true, true);
                }
                return;
            }
            if (cxt.isPlaying) {
                console.log("wav file is playing...");
                return;
            }

            item.sound.once("play", function () {
                var id = item.ui_element_id;
                cxt.isPlaying = true;
                if (id != null) {
                    document.getElementById(id).style.background = "aquamarine";
                    document.getElementById(id).scrollIntoView({ behavior: "smooth", block: "center" });
                }
            });
            item.sound.once("end", function () {
                var id = item.ui_element_id;
                cxt.isPlaying = false;
                if (id != null) {
                    document.getElementById(id).style.background = "none";
                }
                var t = cxt.newsBroadcastQueue.dequeue();
                console.log("新闻播报完成：", t);
                if (cxt.newsBroadcastQueue.size() == 0) {
                    cxt.stopBroadcastNews();
                    console.log("全部新闻播报完成，清除定时器");
                }
            });
            item.sound.once("stop", function () {
                var id = item.ui_element_id;
                cxt.isPlaying = false;
                if (id != null) {
                    document.getElementById(id).style.background = "none";
                }
            });
            item.sound.once("loaderror", function () {
                var t = cxt.newsBroadcastQueue.dequeue();
                cxt.speek("发生了读取错误", true, true);
                console.log("wav file load error", t);
            });
            item.sound.once("playerror", function () {
                var t = cxt.newsBroadcastQueue.dequeue();
                cxt.speek("发生了读取错误", true, true);
                console.log("wav file play error", t);
            });

            item.sound.play();

            /*** 缓冲下面的TTS语音 ***/
            this.newsBroadcastQueue.front_n(this.tts_preload_threshold).forEach((e) => {

                if (e.sound.state() == "unloaded") {
                    e.sound.load();
                    e.start_load_timestamp = new Date();
                    console.log("preload:", e);
                }
            });

        },
        add_to_broadcast_queue(text, id = null) {
            if (text.match(/^\s+$/)) return; //ignore empty string
            var need_preload = this.newsBroadcastQueue.size() < this.tts_preload_threshold;//前几个需要预加载
            this.newsBroadcastQueue.enqueue({
                text_to_speek: text,
                ui_element_id: id,
                start_load_timestamp: need_preload ? new Date() : null,
                sound: new Howl({
                    src: [encodeURI(`${this.get_http_base_url()}/tts?text=${text}`)],
                    html5: false,
                    preload: need_preload,
                    autoplay: false,
                    loop: false,
                    volume: 1,
                    format: ['wav'],
                    onload: function () { console.log("wav file loaded..."); },
                })
            });
        },
        broadcastSplited(t) {
            t.forEach((item) => {
                switch (item.type) {
                    case "sub_sentence":
                        this.add_to_broadcast_queue(`${item.text}`, item.id);
                        break
                    case "punctuation":
                        break
                }
            });
        },
        initBroadcastNews() {
            this.add_to_broadcast_queue("下面开始播报新闻", "bk-img");
            this.add_to_broadcast_queue(`${this.news.title}`, "title");
            this.add_to_broadcast_queue(`${this.news.source}`, "source");
            /****  摘要Summary  ****/
            this.broadcastSplited(this.news.summary.splited);
            this.add_to_broadcast_queue("下面开始播报新闻正文");
            /****  正文Content  ****/
            this.news.content.forEach((item) => {
                switch (item.type) {
                    case "paragraph":
                        this.broadcastSplited(item.splited);
                        break
                    case "title":
                        this.add_to_broadcast_queue(`${item.text}`, item.id);
                        break
                    default:
                        break
                }
            });
            this.add_to_broadcast_queue("新闻播报完毕");

            console.log(this.newsBroadcastQueue);
        },
        toggleNewsBroadcast() {
            if (this.news_broadcast_interval) {
                this.stopBroadcastNews();
            } else {
                this.startBroadcastNews();
            }
        },
        startBroadcastNews() {
            this.initBroadcastNews();
            this.news_broadcast_interval = setInterval(() => {
                this.broadcast();
            }, 500);
        },
        stopBroadcastNews() {
            clearInterval(this.news_broadcast_interval);
            this.news_broadcast_interval = null;
            var item = this.newsBroadcastQueue.front();
            if (item) item.sound.stop();
            this.newsBroadcastQueue.clear();
        },
        playPauseNewsBroadcast() {
            this.news_broadcast_paused = !this.news_broadcast_paused;
            var item = this.newsBroadcastQueue.front();
            if (this.news_broadcast_paused) {
                item.sound.pause();
                this.speek("暂停", true, true);
            } else {
                item.sound.play();
            }
        },
        backwardNewsBroadcast() {
            var item = this.newsBroadcastQueue.front();
            item.sound.stop();
            this.newsBroadcastQueue.back();
        },
        forwardNewsBroadcast() {
            var item = this.newsBroadcastQueue.front();
            item.sound.stop();
            this.newsBroadcastQueue.dequeue();
        },
        toggle_favorite() {
            var params = new URLSearchParams();
            params.append("news_id", this.news.id);
            params.append("payload", !this.news.favorited);
            params.append('token', this.get_token());
            toggleFavorite(params).then(res => {
                this.toast(res.description);
                if (res.success) {
                    this.news.favorited = res.result;
                }
            });
        },
        toggle_like() {
            var params = new URLSearchParams();
            params.append("news_id", this.news.id);
            params.append("payload", !this.news.liked);
            params.append('token', this.get_token());
            toggleLike(params).then(res => {
                this.toast(res.description);
                if (res.success) {
                    this.news.liked = res.result;
                }
            });
        },
        fetch_related_news() {
            var query_str = '';
            this.news.tags.forEach((tag) => {
                query_str += `${tag} `;
            });
            //console.log(query_str);
            var params = new URLSearchParams();
            params.append('payload', query_str + this.news.title);
            params.append('limit', 10);
            relatedNews(params).then(res => {
                console.log(res);
                if (res.success) {
                    res.data.forEach((item) => {
                        if (item.id != this.news.id) {
                            this.related_news_list.push(item);
                        }
                    });
                    console.log(this.related_news_list);
                } else {
                    console.log(res.description);
                }
            });
        },
    },
    mounted() {
        cxt = this;
        window.cxt = this;
        this.newsId = this.getNewsId();
        this.getNews();
        this.fetchComment();
        this.open_ws_connection();

    },
});
</script>


<style scoped>
* {
    word-break: break-all;
}

.block {
    margin: 0;
    padding: 0 20px;
    color: black;
    overflow-x: hidden;
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

.page {
    box-sizing: border-box;
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    transform: none;
    z-index: 1;
    overflow-x: hidden;
    overflow-y: scroll;
}

.post-infos {
    margin-bottom: 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.post-category {
    font-size: 14px;
    color: white;
    background: #ff2d55;
    display: inline-block;
    font-weight: 600;
    line-height: 18px;
    border-radius: 4px;
    padding: 2px 7px;
    text-transform: uppercase;
}

.close-button {
    position: absolute;
    z-index: 10;
    display: flex;
    width: 28px;
    height: 28px;
    align-items: center;
    justify-content: center;
    background: #595959;
    border-radius: 20px;
    right: 20px;
    top: 42px;
}

.single .article {
    padding: 25px 20px 0 20px;
}

.single .post-infos {
    margin-bottom: 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.single h1 {
    font-size: 30px;
    line-height: 40px;
    margin: 25px 0 25px 0 !important;
}

.single p,
.single ul {
    color: black;
    text-align: justify;
    font-size: 19px;
    line-height: 29px;
    margin: 15px 0 !important;
    text-indent: 2em;
}

.single img {
    width: 100%;
}

.image-with-text {
    margin-top: 10px;
    margin-bottom: 10px;
}

.image-with-text img {
    margin: 0;
    border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
}

.image-text {
    background: #f1f4f6;
    padding: 13px 18px;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
    margin-top: -5px;
    text-align: center;
}

.blockquote {
    margin: 20px auto;
    font-family: Open Sans;
    font-style: italic;
    color: #555555;
    padding: 1.2em 10px 1.2em 40px;
    border-left: 8px solid #78C0A8;
    line-height: 1.6;
    position: relative;
    background: #EDEDED;
}

#summary {
    line-height: 1.6;
    font-size: 18px;
    text-indent: 0%;
    color: #555555;
}

.blockquote:before {
    font-family: Arial;
    content: "\201C";
    color: #78C0A8;
    font-size: 4em;
    position: absolute;
    left: 10px;
    top: -10px;

}

.blockquote::after {
    content: "";
}

.blockquote>span {
    display: block;
    color: #333333;
    font-style: normal;
    font-weight: bold;
    margin-top: 1em;
}

.title-medium-container {
    margin-top: 30px;
    position: relative;
}

.title-medium-container h2 {
    margin: 0;
    font-size: 22px;
    position: relative;
    padding: 10px 0;
}

.social-buttons {
    display: flex;
    justify-content: space-between;
    margin-top: 5px;
}

.big-button.facebook {
    background-color: #3b5998;
    color: #fff !important;
}

.big-button.twitter {
    background-color: #00aced;
    color: #fff !important;
}

.social-buttons .big-button {
    width: calc(50% - 5px);
    height: 40px;
}

.big-button {
    font-size: 16px;
    padding: 10px;
    height: 45px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    font-weight: 600;
}

.author-block {
    display: flex;
    align-items: center;
    background: #f2f2f4;
    padding: 15px 20px;
    position: relative;
    border-radius: 10px;
    justify-content: center;
    height: 12%;
}

.author-block img {
    width: 55px;
    border-radius: 30px;
}

.author-infos {
    margin-left: 15px;
}

.author-block .author-name {
    font-size: 18px;
    font-weight: 600;
    color: #ff2e54;
}

.author-block .author-description {
    font-size: 10px;
    color: #8e8e8e;
}

.card {
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    width: 100%;

    margin: 0;
    box-shadow: none;
    cursor: pointer;
    overflow: hidden;
}

.card-image {
    border-radius: 5px;
    height: 25vh;
}

.card-infos {
    width: 100%;
    position: absolute;
    background-image: linear-gradient(to bottom, rgba(0, 0, 0, 0) 0, rgba(0, 0, 0, 0.8) 100%, rgba(0, 0, 0, 0.9) 100%);
    padding-top: 50px;
    padding-bottom: 15px;
    border-bottom-left-radius: 5px;
    border-bottom-right-radius: 5px;
    z-index: 2;
}

.card-title {
    color: #fff;
    padding-left: 15px;
    padding-right: 15px;
    margin: 0;
    font-size: 18px;
    line-height: 23px;
}


.commentSwiper {
    width: 75vw;
    height: 100vw;
    overflow-y: clip;
    margin-top: 20px;
    margin-bottom: 40px;
}

.commentSwiper .swiper-slide {
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 18px;
    font-size: 22px;
    font-weight: bold;
    color: rgb(0, 0, 0);
    background-color: #EDEDED;
}



.comment {
    position: absolute;
    width: 100%;
    height: 100%;
    overflow: hidden;
}

.comment .content {
    position: absolute;
    color: black;
    padding: 10px;
    padding-top: 2px;
    font-size: 20px;
    text-align: justify;
    display: flex;
    height: 62%;
    overflow-y: scroll;
}


.foot-banner {
    display: flex;
    width: 100%;
    height: 3rem;
    background: #f4f4f7;
    position: absolute;
    bottom: 0;
    height: 13%;
}

.foot-banner-item {
    line-height: 3rem;
    font-size: 1rem;
    text-align: center;
    display: inline-block;
    flex: 1;
    color: #333333;
    border-top: 2px solid #ebe8e8;
    transition: all 0.5s;
    -moz-transition: all 0.5s;
    -webkit-transition: all 0.5s;
    -o-transition: all 0.5s;
}

.foot-banner-item:not(:last-child) {
    border-right: 2px solid #ebe8e8;
}

.foot-banner-item:not(:first-child) {
    border-left: 2px solid #ebe8e8;
}

.foot-banner img {
    display: inline-block;
    height: 1.5rem;
    width: fit-content;
    margin-right: 5px;
    vertical-align: middle;
}

.almostTransparent {
    opacity: 0.2;
}

.sub-box {
    position: fixed;
    z-index: 1;
    right: 10px;
    bottom: 5px;
    transition: .5s;
}

.fab {
    color: #fff;
    -webkit-border-radius: 100%;
    border-radius: 100%;
    background-color: rgba(0, 0, 0, .5);
    font-size: 30px;
    line-height: 45px;
    position: relative;
    display: inline-block;
    width: 45px;
    height: 45px;
    cursor: pointer;
    text-align: center;
}

.on {
    background-color: rgba(247, 207, 30, 0.9);
    color: #333333;
}

.sub-box>div {
    visibility: hidden;
    pointer-events: none;
    opacity: 0;
    transition: .5s;
    margin-bottom: 7px;
    transition: .5s;
}

.sub-box.show>div {
    visibility: visible;
    pointer-events: auto;
    opacity: 1;
}

.img-bottom-banner {
    position: absolute;
    display: flex;
    /*margin-top: -55px;*/
    top: 0;
    right: 0;
}

.img-bottom-banner>div {
    margin-right: 5px;
    margin-left: 5px;
    margin-top: 5px;
}

.control-pannel {
    display: flex;
    position: fixed;
    bottom: 10px;
    flex-direction: row;
    justify-content: space-around;
    align-items: center;
    height: 80px;
    right: 0;
    left: 0;
    width: 60vw;
    z-index: 2;
    background: #e0e5ec;
    box-shadow: -7px -7px 20px 0px #fff9, -4px -4px 5px 0px #fff9, 7px 7px 20px 0px #0002, 4px 4px 5px 0px #0001, inset 0px 0px 0px 0px #fff9, inset 0px 0px 0px 0px #0001, inset 0px 0px 0px 0px #fff9, inset 0px 0px 0px 0px #0001;
    transition: box-shadow 0.6s cubic-bezier(.79, .21, .06, .81);
    border-radius: 10px;
    margin: 0 auto;
}

.btn {
    height: 50px;
    width: 50px;
    border-radius: 3px;
    background: #e0e5ec;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
    -webkit-tap-highlight-color: transparent;
    box-shadow:
        -7px -7px 20px 0px #fff9,
        -4px -4px 5px 0px #fff9,
        7px 7px 20px 0px #0002,
        4px 4px 5px 0px #0001;
    transition: box-shadow 0.6s cubic-bezier(.79, .21, .06, .81);
    font-size: 26px;
    color: #666;
    text-decoration: none;
}

.btn:active {
    box-shadow: 4px 4px 6px 0 rgba(255, 255, 255, .5),
        -4px -4px 6px 0 rgba(116, 125, 136, .2),
        inset -4px -4px 6px 0 rgba(255, 255, 255, .5),
        inset 4px 4px 6px 0 rgba(116, 125, 136, .3);
}

.fab-large {
    font-size: 35px;
    line-height: 55px;
    width: 55px;
    height: 55px;
}
</style>
