/* eslint-disable no-unused-vars */

import axios from "axios";
import { get, post, getImg, getFile, postFile } from "./http";

/**
 * PING TEST
 * @returns
 */
export const ping = () => get(`/ping`);
export const getNewsByCategory = (v,params) => get(`/news/${v}`,params);
export const getDetailedNews = (params) => get(`/news/detail`,params);
export const postComment = (params) => post(`/comment/post`,params);
export const getComment = (params) => get(`/comment/get`,params);
export const performCommentOperation = (params) => post(`/comment/operation`,params);
export const toggleFavorite = (params) => post(`/news/favorite`,params);
export const toggleLike = (params) => post(`/news/like`,params);
export const searchNews = (params) => get(`/news/search`,params);
export const getTrending = (params) => get(`/news/trending`,params);
export const getFavorite = (params) => get(`/user/favorite`,params);
export const relatedNews = (params) => get(`/news/related`,params);