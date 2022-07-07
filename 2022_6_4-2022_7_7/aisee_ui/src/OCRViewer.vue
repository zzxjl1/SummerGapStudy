<template>
    <h2>
        <span v-for="(item, item_index) in data" :key="item_index" :id="item.id">
            {{ item.text }}
        </span>
    </h2>

    <div style="height:80px"></div>
    
    <div class="sub-box show">
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
</template>
<script>
import queue from '@/plugins/queue';
import { Howl } from 'howler';
import "@/assets/home/iconfont.css";
export default ({
    data() {
        return {
            data: null,
            newsBroadcastQueue: queue,
            tts_preload_threshold: 2,
            news_broadcast_interval: null,
            news_broadcast_paused: false,
            isPlaying: false,
        }
    },
    mounted() {
        this.fetch();
        this.toggleNewsBroadcast();
    },
    methods: {
        splitParagraph(text) {
            var result = [];
            var temp = '';
            for (var i = 0; i < text.length; i++) {
                if (text[i] == '。' || text[i] == '，' || text[i] == '；' || text[i] == '？' || text[i] == '！') {
                    result.push({ type: 'sub_sentence', text: temp });
                    result.push({ type: 'punctuation', text: text[i] });
                    temp = '';
                } else {
                    temp += text[i];
                }
            }
            if (temp != '') { result.push({ type: 'sub_sentence', text: temp }); }

            result.forEach((item, index) => {
                item["id"] = index;
            });
            return result;
        },
        fetch() {
            var t;
            try {
                // eslint-disable-next-line no-undef
                t = JS.fetch();
            } catch (e) {
                t = "测试，test。123！";
            }
            this.data = this.splitParagraph(t);
        },
        broadcast() {
            if (this.news_broadcast_paused) return;

            var item = this.newsBroadcastQueue.front();

            if (item.sound.state() == "unloaded" && !item.sound._preload) {
                item.start_load_timestamp = new Date();
                item.sound.load();
                return;
            }
            if (item.sound.state() == "loading") {
                console.log("wav file is still loading...");
                //TIME DIFFERENCE IN SECONDS
                var timeDiff = (new Date() - item.start_load_timestamp) / 1000;
                if (timeDiff > 10) {
                    var t = this.newsBroadcastQueue.dequeue();
                    console.log("wav file loading timeout", t);
                    this.$utils.speek("发生了读取错误", true, true);
                }
                return;
            }
            if (this.isPlaying) {
                console.log("wav file is playing...");
                return;
            }
            var cxt = this;
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
                cxt.$utils.speek("发生了读取错误", true, true);
                console.log("wav file load error", t);
            });
            item.sound.once("playerror", function () {
                var t = cxt.newsBroadcastQueue.dequeue();
                cxt.$utils.speek("发生了读取错误", true, true);
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
                    src: [encodeURI(`${this.$utils.get_http_base_url()}/tts?text=${text}`)],
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
            this.add_to_broadcast_queue("下面开始播报");
            /****  正文Content  ****/
            this.broadcastSplited(this.data);

            this.add_to_broadcast_queue("播报完毕");

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
                this.$utils.speek("暂停", true, true);
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
    },
})
</script>
<style scoped>
h2 {
    text-align: justify;
    word-break: break-all;
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
