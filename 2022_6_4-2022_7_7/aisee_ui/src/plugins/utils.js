function speek(text, preemptive, flush) {
  try {
    // eslint-disable-next-line no-undef
    JS.speek(text, preemptive, flush);
  } catch (e) {
    console.log(text);
  }
}
function toast(t) {
  try {
    // eslint-disable-next-line no-undef
    JS.toast(t);
  } catch (e) {
    console.log(t);
  }
}
function get_token() {
  var token;
  try {
    // eslint-disable-next-line no-undef
    token = JS.get_token();
  } catch (e) {
    token = "KpMP6U1nySvocbAWdtx4qhTZgHmFuVRi";
  }
  return token;
}
function showNewsDetail(id) {
  try {
    // eslint-disable-next-line no-undef
    JS.showNewsDetail(id);
  } catch (e) {
    location.href = `/newsviewer.html?id=${id}`;
    console.log(e);
  }

  console.log(id);
}
function get_http_base_url() {
  var http_base_url;
  try {
    // eslint-disable-next-line no-undef
    http_base_url = JS.get_httpBaseUrl();
  } catch (e) {
    http_base_url = "http://192.168.31.114:4000";
  }
  return http_base_url;
}
function get_ws_base_url() {
  var ws_base_url;
  try {
    // eslint-disable-next-line no-undef
    ws_base_url = JS.get_wsBaseUrl();
  } catch (e) {
    ws_base_url = "ws://192.168.31.114:4000";
  }
  return ws_base_url;
}
export default {
  speek,
  toast,
  get_token,
  showNewsDetail,
  get_http_base_url,
  get_ws_base_url,
};
