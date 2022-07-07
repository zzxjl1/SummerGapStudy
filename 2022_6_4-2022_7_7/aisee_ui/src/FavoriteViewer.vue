<template>

    <div class="block">
        <ul class="list media-list post-list">
            <li v-for="news in data" :key="news.id">
                <a @click="$utils.showNewsDetail(news.id)">
                    <div class="item-content">
                        <div class="item-media"><img :src="news.bk_img"></div>
                        <div class="item-inner">
                            <div class="item-subtitle">{{ news.category }}</div>
                            <div class="item-title">{{ news.title }}</div>
                            <div class="item-subtitle bottom-subtitle">{{ news.created_at }}</div>
                        </div>
                    </div>
                </a>
            </li>
        </ul>
        <h3 v-if="data">没有更多了</h3><br>
        <loading :active="isLoading" :can-cancel="false" :is-full-page="true" :opacity="1" />
    </div>
</template>
<script>
import { getFavorite } from '@/api/index';
import Loading from 'vue-loading-overlay';
import 'vue-loading-overlay/dist/vue-loading.css';

export default ({
    data() {
        return {
            data: null,
            isLoading: false,
        }
    },
    components: {
        Loading,
    },
    methods: {
        fetch() {
            var params = new URLSearchParams();
            params.append('token', this.$utils.get_token());
            var description = '';
            this.isLoading = true;
            getFavorite(params).then(res => {
                console.log(res);
                if (res.success) {
                    this.data = res.result;
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
                        confirmButtonText: '重试',
                        allowOutsideClick: false,
                    }).then((result) => {
                        if (result.isConfirmed) {
                            console.log(result);
                            this.fetch();
                        }
                    });
                }
            });
        }
    },
    mounted() {
        this.fetch();
    },

})
</script>

<style scoped>
* {
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -khtml-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
}

h3 {
    text-align: center;
}

.block {
    margin: 0;
    padding: 0 20px;
    /* color: #8A8A8F; */
}

.post-list {
    margin: 0;
    padding: 0;
    list-style: none;
}

.post-list li {
    cursor: pointer;
}

.post-list .item-content .item-media {
    width: 40%;
}

.post-list .item-content .item-media img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 5px;
}

.post-list .item-subtitle {
    color: #a6a6ab;
    text-transform: uppercase;
    font-weight: 600;
    font-size: 14px;
    display: flex;
}

.post-list .item-title {
    margin: 5px 0 6px;
    color: #000;
    font-weight: 600;
    font-size: 18px;
    line-height: 23px;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
    white-space: pre-wrap;
    text-align: left;
}

.post-list.long-title .item-title {
    -webkit-line-clamp: 3;
}

.post-list .item-subtitle.bottom-subtitle {
    display: flex;
    align-items: center;
    text-transform: none;
    font-weight: 500;
    font-size: 15px;
}

.post-list .item-subtitle.bottom-subtitle i {
    font-weight: 500;
    font-size: 15px;
    margin-right: 5px;
    color: #a6a6ab;
}

.post-list .item-subtitle.bottom-subtitle img {
    width: 22px;
    border-radius: 11px;
    margin-right: 6px;
}

.list .item-content {
    display: flex;
    justify-content: space-between;
    box-sizing: border-box;
    align-items: center;
    min-height: 44px;
    padding-bottom: 10px;
    padding-top: 10px;
}

.item-media {
    display: flex;
    flex-shrink: 0;
    flex-wrap: nowrap;
    align-items: center;
    box-sizing: border-box;
}

.item-inner {
    margin-left: 8px;
}

.close-button {
    position: fixed;
    z-index: 2147483647;
    display: flex;
    width: 40px;
    height: 40px;
    align-items: center;
    justify-content: center;
    background: #595959;
    border-radius: 20px;
    right: 15px;
    top: 15px;
    opacity: 0.8;
}

.close-button img {
    width: 25px;
    height: 25px;
}
</style>