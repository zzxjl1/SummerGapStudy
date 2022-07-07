<template>
    <div class="card">
        <img class="card-image" :src="bk_img ? bk_img : 'https://mdbcdn.b-cdn.net/img/new/fluid/city/018.webp'">
        <div class="card-infos">

            <div class="card-date">
                <span class="iconfont icon-clock"></span>&nbsp;
                <timeago :datetime="created_at" />
            </div>
            <div class="tags">

                <span v-for="(tag, index) in tags" :key="index" style="background-color: #ff2d55;" class="chip">{{ tag
                }}</span>

            </div>
            <h2 class="card-title">{{ title }}</h2>
            <div class="card-bottom">
                <div class="card-source">
                    <div>来源于 {{ source }}</div>
                </div>
                <div class="card-statistics">
                    <span class="iconfont icon-view"></span>{{ click_count }}
                    <span class="iconfont icon-like-fill"></span>{{ like_count }}
                    <span class="iconfont icon-comment"></span>{{ comment_count }}
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import "@/assets/home/iconfont.css";
export default {
    name: "NewsItem",
    data() {
        return {
        }
    },
    props: {
        source: String,
        title: String,
        tags: Array,
        created_at: String,
        click_count: Number,
        like_count: Number,
        comment_count: Number,
        bk_img: String,
    },
}
</script>
<style scoped>
.card {
    position: relative;
    width: 95%;
    height: 95%;
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
    box-shadow: 0 10px 20px rgb(0 0 0 / 19%), 0 6px 6px rgb(0 0 0 / 23%);
}

.card-image {
    object-fit: cover;
    width: 100%;
    height: 100%;
    position: absolute;
    border-radius: 15px;
}

.card:active {
    transform: scale(0.95);
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
    font-size: 28px;
    line-height: 36px;
}

.tags {
    position: absolute;
    top: 15px;
    right: 15px;
    height: 23px;
    overflow: hidden;
}

.chip {
    float: right;
    padding: 0 10px;
    margin-left: 10px;
    text-transform: uppercase;
    font-weight: 500;
    font-size: 12px;
    display: flex;
    line-height: 23px;
    border-radius: 10px;
    color: white;
}

.card-bottom {
    display: flex;
    align-items: center;
    margin-top: 12px;
    justify-content: space-between;
    color: rgba(255, 255, 255, 0.8);
    font-weight: 500;
    font-size: 16px;
}

.card-source {
    display: flex;
    align-items: center;
}

.card-statistics {
    display: flex;
    align-items: center;
    line-height: 0;
}

.card-statistics span {
    margin-right: 5px;
    margin-left: 10px;
    font-size: 16px;
}

.card .card-date {
    margin-bottom: 5px;
    color: #e0e0e0;
    font-weight: 500;
    font-size: 15px;
    display: flex;
    align-items: center;
}

.card-category {
    color: #b9b9b9;
    font-weight: 600;
    font-size: 16px;
    margin-bottom: 4px;
    text-transform: uppercase;
}
</style>
