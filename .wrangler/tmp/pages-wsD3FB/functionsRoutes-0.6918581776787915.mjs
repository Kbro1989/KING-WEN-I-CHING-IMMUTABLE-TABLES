import { onRequestGet as __api_cache_layer__id__js_onRequestGet } from "C:\\Users\\krist\\Desktop\\KING-WEN-I-CHING-IMMUTABLE-TABLES\\functions\\api\\cache\\layer\\[id].js"
import { onRequestGet as __api_hexagram__id__js_onRequestGet } from "C:\\Users\\krist\\Desktop\\KING-WEN-I-CHING-IMMUTABLE-TABLES\\functions\\api\\hexagram\\[id].js"
import { onRequestGet as __api_jkd__id__js_onRequestGet } from "C:\\Users\\krist\\Desktop\\KING-WEN-I-CHING-IMMUTABLE-TABLES\\functions\\api\\jkd\\[id].js"
import { onRequestGet as __api_world_js_onRequestGet } from "C:\\Users\\krist\\Desktop\\KING-WEN-I-CHING-IMMUTABLE-TABLES\\functions\\api\\world.js"
import { onRequest as __api_kingwen_link_js_onRequest } from "C:\\Users\\krist\\Desktop\\KING-WEN-I-CHING-IMMUTABLE-TABLES\\functions\\api\\kingwen-link.js"
import { onRequestGet as __widget__id__js_onRequestGet } from "C:\\Users\\krist\\Desktop\\KING-WEN-I-CHING-IMMUTABLE-TABLES\\functions\\widget\\[id].js"
import { onRequest as ___middleware_js_onRequest } from "C:\\Users\\krist\\Desktop\\KING-WEN-I-CHING-IMMUTABLE-TABLES\\functions\\_middleware.js"

export const routes = [
    {
      routePath: "/api/cache/layer/:id",
      mountPath: "/api/cache/layer",
      method: "GET",
      middlewares: [],
      modules: [__api_cache_layer__id__js_onRequestGet],
    },
  {
      routePath: "/api/hexagram/:id",
      mountPath: "/api/hexagram",
      method: "GET",
      middlewares: [],
      modules: [__api_hexagram__id__js_onRequestGet],
    },
  {
      routePath: "/api/jkd/:id",
      mountPath: "/api/jkd",
      method: "GET",
      middlewares: [],
      modules: [__api_jkd__id__js_onRequestGet],
    },
  {
      routePath: "/api/world",
      mountPath: "/api",
      method: "GET",
      middlewares: [],
      modules: [__api_world_js_onRequestGet],
    },
  {
      routePath: "/api/kingwen-link",
      mountPath: "/api",
      method: "",
      middlewares: [],
      modules: [__api_kingwen_link_js_onRequest],
    },
  {
      routePath: "/widget/:id",
      mountPath: "/widget",
      method: "GET",
      middlewares: [],
      modules: [__widget__id__js_onRequestGet],
    },
  {
      routePath: "/",
      mountPath: "/",
      method: "",
      middlewares: [___middleware_js_onRequest],
      modules: [],
    },
  ]