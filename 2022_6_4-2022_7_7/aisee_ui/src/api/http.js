/* eslint-disable no-undef */
import axios from "axios";
axios.defaults.timeout = 60000; //超时时间设置
axios.defaults.withCredentials = true; //设置跨域请求时是否需要使用凭证
//Content-Type 响应头
axios.defaults.headers.post["Content-Type"] = "application/json;charset=UTF-8";
try {
  // eslint-disable-next-line no-undef
  axios.defaults.baseURL = JS.get_httpBaseUrl();
} catch (e) {
  axios.defaults.baseURL = "http://localhost:4000";
}



/**
 * 封装get方法
 * @param url
 * @param data
 * @returns {Promise}
 */

export function get(url, params = {}) {
  return new Promise((resolve, reject) => {
    axios
      .get(url, {
        params: params,
      })
      .then((response) => {
        resolve(response.data);
      })
      .catch((err) => {
        reject(err);
      });
  });
}

/**
 * 封装getImg方法
 * @param url
 * @param data
 * @returns {Promise}
 */

export function getImg(url, params = {}) {
  return new Promise((resolve, reject) => {
    axios
      .get(url, {
        params: params,
        responseType: "blob", //接收的值类型
      })
      .then((response) => {
        resolve(response.data);
      })
      .catch((err) => {
        reject(err);
      });
  });
}

/**
 * 封装getFile方法
 * @param url
 * @param data
 * @returns {Promise}
 */

export function getFile(url, params = {}) {
  return new Promise((resolve, reject) => {
    axios
      .get(url, {
        params: params,
        responseType: "blob", //接收的值类型
      })
      .then((response) => {
        resolve(response);
      })
      .catch((err) => {
        reject(err);
      });
  });
}

/**
 * 封装post请求
 * @param url
 * @param data
 * @returns {Promise}
 */

export function post(url, data = {}) {
  return new Promise((resolve, reject) => {
    axios.post(url, data).then(
      (response) => {
        resolve(response.data);
      },
      (err) => {
        reject(err);
      }
    );
  });
}

/**
 * 封装带文件上传的post请求
 * @param url
 * @param data
 * @returns {Promise}
 */

export function postFile(url, data = {}) {
  return new Promise((resolve, reject) => {
    axios
      .post(url, data, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      .then(
        (response) => {
          resolve(response.data);
        },
        (err) => {
          reject(err);
        }
      );
  });
}

/**
 * 封装delete请求
 * @param url
 * @param data
 * @returns {Promise}
 */

export function deletes(url, data = {}) {
  return new Promise((resolve, reject) => {
    axios.delete(url, data).then(
      (response) => {
        resolve(response.data);
      },
      (err) => {
        reject(err);
      }
    );
  });
}

/**
 * 封装put请求
 * @param url
 * @param data
 * @returns {Promise}
 */

export function put(url, data = {}) {
  return new Promise((resolve, reject) => {
    axios.put(url, data).then(
      (response) => {
        resolve(response.data);
      },
      (err) => {
        reject(err);
      }
    );
  });
}
