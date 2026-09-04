// <define:__ROUTES__>
var define_ROUTES_default = {
  version: 1,
  include: [
    "/api/*",
    "/widget/*"
  ],
  exclude: [
    "/*.html",
    "/favicon.ico"
  ]
};

// ../../AppData/Local/npm-cache/_npx/32026684e21afda6/node_modules/wrangler/templates/pages-dev-pipeline.ts
import worker from "C:\\Users\\krist\\Desktop\\KING-WEN-I-CHING-IMMUTABLE-TABLES\\.wrangler\\tmp\\pages-DsQhWz\\functionsWorker-0.46526767259612556.mjs";
import { isRoutingRuleMatch } from "C:\\Users\\krist\\AppData\\Local\\npm-cache\\_npx\\32026684e21afda6\\node_modules\\wrangler\\templates\\pages-dev-util.ts";
export * from "C:\\Users\\krist\\Desktop\\KING-WEN-I-CHING-IMMUTABLE-TABLES\\.wrangler\\tmp\\pages-DsQhWz\\functionsWorker-0.46526767259612556.mjs";
var routes = define_ROUTES_default;
var pages_dev_pipeline_default = {
  fetch(request, env, context) {
    const { pathname } = new URL(request.url);
    for (const exclude of routes.exclude) {
      if (isRoutingRuleMatch(pathname, exclude)) {
        return env.ASSETS.fetch(request);
      }
    }
    for (const include of routes.include) {
      if (isRoutingRuleMatch(pathname, include)) {
        const workerAsHandler = worker;
        if (workerAsHandler.fetch === void 0) {
          throw new TypeError("Entry point missing `fetch` handler");
        }
        return workerAsHandler.fetch(request, env, context);
      }
    }
    return env.ASSETS.fetch(request);
  }
};
export {
  pages_dev_pipeline_default as default
};
//# sourceMappingURL=l5lhbgs85g.js.map
