/**
 * anti-vpn-detect.js — 去代理头脚本（Loon http-request）
 *
 * 作用：去掉请求里可能暴露代理的头，让应用的检测接口更难
 * 从请求头判断出流量经过代理。
 *
 * 注意：真正决定性的还是出口 IP 本身。服务端直接按 IP 判断
 * （机房段黑名单）的，这个脚本拦不住，那得换住宅 IP 才行。
 * 本脚本只处理请求头层面的暴露点。
 */

const PROXY_HEADERS = [
  "x-forwarded-for",
  "x-forwarded-host",
  "x-forwarded-proto",
  "x-real-ip",
  "via",
  "proxy-connection",
  "proxy-authorization",
  "x-proxy-id",
  "cf-connecting-ip",
  "true-client-ip",
  "x-original-forwarded-for",
];

const headers = $request.headers || {};
let changed = false;

for (const name of PROXY_HEADERS) {
  for (const key of Object.keys(headers)) {
    if (key.toLowerCase() === name) {
      delete headers[key];
      changed = true;
    }
  }
}

if (changed) {
  $done({ headers });
} else {
  $done({});
}
