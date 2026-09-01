
<!doctype html>
<html lang="en" class="no-js">
  <head>
    
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width,initial-scale=1">
      
        <meta name="description" content="FastAPI framework, high performance, easy to learn, fast to code, ready for production">
      
      
      
        <link rel="canonical" href="https://fastapi.tiangolo.com/advanced/custom-response/">
      
      
        <link rel="prev" href="../response-directly/">
      
      
        <link rel="next" href="../additional-responses/">
      
      
        
          <link rel="alternate" href="/" hreflang="en">
        
          <link rel="alternate" href="/de/" hreflang="en">
        
          <link rel="alternate" href="/es/" hreflang="en">
        
          <link rel="alternate" href="/fr/" hreflang="en">
        
          <link rel="alternate" href="/hi/" hreflang="en">
        
          <link rel="alternate" href="/ja/" hreflang="en">
        
          <link rel="alternate" href="/ko/" hreflang="en">
        
          <link rel="alternate" href="/pt/" hreflang="en">
        
          <link rel="alternate" href="/ru/" hreflang="en">
        
          <link rel="alternate" href="/tr/" hreflang="en">
        
          <link rel="alternate" href="/uk/" hreflang="en">
        
          <link rel="alternate" href="/zh/" hreflang="en">
        
          <link rel="alternate" href="/zh-hant/" hreflang="en">
        
      
      
      <link rel="icon" href="../../img/favicon.png">
      <meta name="generator" content="zensical-0.0.51">
    
    
      
        <title>Custom Response - HTML, Stream, File, others - FastAPI</title>
      
    
    
      
        
      
      <link rel="stylesheet" href="../../assets/stylesheets/classic/main.f62f0af6.min.css">
      
        
          
        
        <link rel="stylesheet" href="../../assets/stylesheets/classic/palette.7dc9a0ad.min.css">
      
      


    
    
      
    
    
      
        
        
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,300i,400,400i,500,500i,700,700i%7CRoboto+Mono:400,400i,700,700i&amp;display=fallback">
        <style>:root{--md-text-font:"Roboto";--md-code-font:"Roboto Mono"}</style>
      
    
    
      <link rel="stylesheet" href="../../css/termynal.css">
    
      <link rel="stylesheet" href="../../css/custom.css">
    
    <script>__md_scope=new URL("../..",location),__md_scope.pathname.endsWith("/")||(__md_scope=new URL(__md_scope.pathname+"/",location)),__md_hash=e=>[...e].reduce(((e,t)=>(e<<5)-e+t.charCodeAt(0)),0),__md_get=(e,t=localStorage,_=__md_scope)=>JSON.parse(t.getItem(_.pathname+"."+e)),__md_set=(e,t,_=localStorage,a=__md_scope)=>{try{_.setItem(a.pathname+"."+e,JSON.stringify(t))}catch(e){}},document.documentElement.setAttribute("data-platform",navigator.platform)</script>
    
      

    
    
  </head>
  
  
    
    
      
    
    
    
    
    <body dir="ltr" data-md-color-scheme="default" data-md-color-primary="indigo" data-md-color-accent="indigo">
  
    
    <input class="md-toggle" data-md-toggle="drawer" type="checkbox" id="__drawer" autocomplete="off">
    <input class="md-toggle" data-md-toggle="search" type="checkbox" id="__search" autocomplete="off">
    <label class="md-overlay" for="__drawer" aria-label="Navigation"></label>
    <div data-md-component="skip">
      
        
        <a href="#custom-response-html-stream-file-others" class="md-skip">
          Skip to content
        </a>
      
    </div>
    <div data-md-component="announce">
      
        <aside class="md-banner">
          <div class="md-banner__inner md-grid md-typeset">
            
            
<div class="announce-wrapper">
  <div id="announce-left">
    <div class="item">
      <a class="announce-link" href="https://fastapicloud.com" target="_blank">
        <span class="twemoji">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M13 19c0 .34.04.67.09 1H6.5c-1.5 0-2.81-.5-3.89-1.57C1.54 17.38 1 16.09 1 14.58q0-1.95 1.17-3.48C3.34 9.57 4 9.43 5.25 9.15c.42-1.53 1.25-2.77 2.5-3.72S10.42 4 12 4c1.95 0 3.6.68 4.96 2.04S19 9.05 19 11c1.15.13 2.1.63 2.86 1.5.51.57.84 1.21 1 1.92A5.9 5.9 0 0 0 19 13c-3.31 0-6 2.69-6 6m3-1h2v4h2v-4h2l-3-3z"/></svg>
        </span> Deploy on <strong>FastAPI Cloud</strong> 🚀
      </a>
    </div>
    <div class="item">
      <a class="announce-link" href="https://fastapiconf.com" target="_blank">
        <span class="twemoji">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19 19H5V8h14m-3-7v2H8V1H6v2H5c-1.1 0-2 .9-2 2v14a2 2 0 0 0 2 2h14c1.11 0 2-.89 2-2V5a2 2 0 0 0-2-2h-1V1m-7.12 11H7.27l2.92 2.11-1.11 3.45L12 15.43l2.92 2.13-1.12-3.44L16.72 12h-3.6L12 8.56z"/></svg>
        </span> <strong>FastAPI Conf '26</strong> — Oct 28, 2026, Amsterdam 🎤
      </a>
    </div>
    <div class="item">
      <a class="announce-link" href="https://x.com/fastapi" target="_blank">
        <span class="twemoji">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free (Icons: CC BY 4.0, Fonts: SIL OFL 1.1, Code: MIT License) Copyright 2026 Fonticons, Inc.--><path fill="currentColor" d="M357.2 48h70.6L273.6 224.2 455 464H313L201.7 318.6 74.5 464H3.8l164.9-188.5L-5.2 48h145.6l100.5 132.9zm-24.8 373.8h39.1L119.1 88h-42z"/></svg>
        </span> Follow <strong>@fastapi</strong> on <strong>X (Twitter)</strong> to stay updated
      </a>
    </div>
    <div class="item">
      <a class="announce-link" href="https://www.linkedin.com/company/fastapi" target="_blank">
        <span class="twemoji linkedin">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free (Icons: CC BY 4.0, Fonts: SIL OFL 1.1, Code: MIT License) Copyright 2026 Fonticons, Inc.--><path fill="currentColor" d="M416 32H31.9C14.3 32 0 46.5 0 64.3v383.4C0 465.5 14.3 480 31.9 480H416c17.6 0 32-14.5 32-32.3V64.3c0-17.8-14.4-32.3-32-32.3M135.4 416H69V202.2h66.5V416zM102.2 96a38.5 38.5 0 1 1 0 77 38.5 38.5 0 1 1 0-77m282.1 320h-66.4V312c0-24.8-.5-56.7-34.5-56.7-34.6 0-39.9 27-39.9 54.9V416h-66.4V202.2h63.7v29.2h.9c8.9-16.8 30.6-34.5 62.9-34.5 67.2 0 79.7 44.3 79.7 101.9z"/></svg>
        </span> Follow <strong>FastAPI</strong> on <strong>LinkedIn</strong> to stay updated
      </a>
    </div>
    <div class="item">
      <a class="announce-link" href="https://fastapi.tiangolo.com/newsletter/">
        <span class="twemoji">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="m20 8-8 5-8-5V6l8 5 8-5m0-2H4c-1.11 0-2 .89-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2"/></svg>
        </span> Subscribe to the <strong>FastAPI and friends</strong> newsletter 🎉
      </a>
    </div>
  </div>
  <div id="announce-right" style="position: relative;">
    <div class="item">
  <a title="BlockBee Cryptocurrency Payment Gateway" style="display: block; position: relative;" href="https://blockbee.io?ref=fastapi" target="_blank">
    <span class="sponsor-badge">sponsor</span>
    <img class="sponsor-image" src="/img/sponsors/blockbee-banner.png" alt="BlockBee Cryptocurrency Payment Gateway" />
  </a>
</div>
<div class="item">
  <a title="Auth, user management and more for your B2B product" style="display: block; position: relative;" href="https://www.propelauth.com/?utm_source=fastapi&utm_campaign=1223&utm_medium=topbanner" target="_blank">
    <span class="sponsor-badge">sponsor</span>
    <img class="sponsor-image" src="/img/sponsors/propelauth-banner.png" alt="Auth, user management and more for your B2B product" />
  </a>
</div>
<div class="item">
  <a title="Deploy & scale any full-stack web app on Render. Focus on building apps, not infra." style="display: block; position: relative;" href="https://docs.render.com/deploy-fastapi?utm_source=deploydoc&utm_medium=referral&utm_campaign=fastapi" target="_blank">
    <span class="sponsor-badge">sponsor</span>
    <img class="sponsor-image" src="/img/sponsors/render-banner.svg" alt="Deploy & scale any full-stack web app on Render. Focus on building apps, not infra." />
  </a>
</div>
<div class="item">
  <a title="Cut Code Review Time & Bugs in Half with CodeRabbit" style="display: block; position: relative;" href="https://www.coderabbit.ai/?utm_source=fastapi&utm_medium=banner&utm_campaign=fastapi" target="_blank">
    <span class="sponsor-badge">sponsor</span>
    <img class="sponsor-image" src="/img/sponsors/coderabbit-banner.png" alt="Cut Code Review Time & Bugs in Half with CodeRabbit" />
  </a>
</div>
<div class="item">
  <a title="Making Retail Purchases Actionable for Brands and Developers" style="display: block; position: relative;" href="https://subtotal.com/?utm_source=fastapi&utm_medium=sponsorship&utm_campaign=open-source" target="_blank">
    <span class="sponsor-badge">sponsor</span>
    <img class="sponsor-image" src="/img/sponsors/subtotal-banner.svg" alt="Making Retail Purchases Actionable for Brands and Developers" />
  </a>
</div>
<div class="item">
  <a title="Deploy enterprise applications at startup speed" style="display: block; position: relative;" href="https://docs.railway.com/guides/fastapi?utm_medium=integration&utm_source=docs&utm_campaign=fastapi" target="_blank">
    <span class="sponsor-badge">sponsor</span>
    <img class="sponsor-image" src="/img/sponsors/railway-banner.png" alt="Deploy enterprise applications at startup speed" />
  </a>
</div>
<div class="item">
  <a title="SerpApi: Web Search API" style="display: block; position: relative;" href="https://serpapi.com/?utm_source=fastapi_website" target="_blank">
    <span class="sponsor-badge">sponsor</span>
    <img class="sponsor-image" src="/img/sponsors/serpapi-banner.png" alt="SerpApi: Web Search API" />
  </a>
</div>
<div class="item">
  <a title="Greptile: The AI Code Reviewer" style="display: block; position: relative;" href="https://www.greptile.com/?utm_source=fastapi&utm_medium=sponsorship&utm_campaign=fastapi_sponsor_page" target="_blank">
    <span class="sponsor-badge">sponsor</span>
    <img class="sponsor-image" src="/img/sponsors/greptile-banner.png" alt="Greptile: The AI Code Reviewer" />
  </a>
</div>
  </div>
</div>

          </div>
          
        </aside>
      
    </div>
    
    
      

  

<header class="md-header md-header--shadow md-header--lifted" data-md-component="header">
  <nav class="md-header__inner md-grid" aria-label="Header">
    <a href="../.." title="FastAPI" class="md-header__button md-logo" aria-label="FastAPI" data-md-component="logo">
      
  <img src="../../img/icon-white.svg" alt="FastAPI">

    </a>
    <label class="md-header__button md-icon" for="__drawer" aria-label="Navigation">
      
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M3 6h18v2H3zm0 5h18v2H3zm0 5h18v2H3z"/></svg>
    </label>
    <div class="md-header__title" data-md-component="header-title">
      <div class="md-header__ellipsis">
        <div class="md-header__topic">
          <span class="md-ellipsis">
            FastAPI
          </span>
        </div>
        <div class="md-header__topic" data-md-component="header-topic">
          <span class="md-ellipsis">
            
              Custom Response - HTML, Stream, File, others
            
          </span>
        </div>
      </div>
    </div>
    
      
        <form class="md-header__option" data-md-component="palette">
  
    
    
    
    <input class="md-option" data-md-color-media="(prefers-color-scheme)" data-md-color-scheme="default" data-md-color-primary="indigo" data-md-color-accent="indigo"  aria-label="Switch to light mode"  type="radio" name="__palette" id="__palette_0">
    
      <label class="md-header__button md-icon" title="Switch to light mode" for="__palette_1" hidden>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M9 2C5.13 2 2 5.13 2 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.87-3.13-7-7-7M6 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H6zm13-8h-2l-3.2 9h1.9l.7-2h3.2l.7 2h1.9zm-2.15 5.65L18 15l1.15 3.65z"/></svg>
      </label>
    
  
    
    
    
    <input class="md-option" data-md-color-media="(prefers-color-scheme: light)" data-md-color-scheme="default" data-md-color-primary="teal" data-md-color-accent="amber"  aria-label="Switch to dark mode"  type="radio" name="__palette" id="__palette_1">
    
      <label class="md-header__button md-icon" title="Switch to dark mode" for="__palette_2" hidden>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2a7 7 0 0 0-7 7c0 2.38 1.19 4.47 3 5.74V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.26c1.81-1.27 3-3.36 3-5.74a7 7 0 0 0-7-7M9 21a1 1 0 0 0 1 1h4a1 1 0 0 0 1-1v-1H9z"/></svg>
      </label>
    
  
    
    
    
    <input class="md-option" data-md-color-media="(prefers-color-scheme: dark)" data-md-color-scheme="slate" data-md-color-primary="teal" data-md-color-accent="amber"  aria-label="Switch to system preference"  type="radio" name="__palette" id="__palette_2">
    
      <label class="md-header__button md-icon" title="Switch to system preference" for="__palette_0" hidden>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2a7 7 0 0 1 7 7c0 2.38-1.19 4.47-3 5.74V17a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 0 1 7-7M9 21v-1h6v1a1 1 0 0 1-1 1h-4a1 1 0 0 1-1-1m3-17a5 5 0 0 0-5 5c0 2.05 1.23 3.81 3 4.58V16h4v-2.42c1.77-.77 3-2.53 3-4.58a5 5 0 0 0-5-5"/></svg>
      </label>
    
  
</form>
      
    
    
      <script>var palette=__md_get("__palette");if(palette&&palette.color){if("(prefers-color-scheme)"===palette.color.media){var media=matchMedia("(prefers-color-scheme: light)"),input=document.querySelector(media.matches?"[data-md-color-media='(prefers-color-scheme: light)']":"[data-md-color-media='(prefers-color-scheme: dark)']");palette.color.media=input.getAttribute("data-md-color-media"),palette.color.scheme=input.getAttribute("data-md-color-scheme"),palette.color.primary=input.getAttribute("data-md-color-primary"),palette.color.accent=input.getAttribute("data-md-color-accent")}for(var[key,value]of Object.entries(palette.color))document.body.setAttribute("data-md-color-"+key,value)}</script>
    
    
      <div class="md-header__option">
  <div class="md-select">
    
    <button class="md-header__button md-icon" aria-label="Select language">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="m12.87 15.07-2.54-2.51.03-.03A17.5 17.5 0 0 0 14.07 6H17V4h-7V2H8v2H1v2h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2zm-2.62 7 1.62-4.33L19.12 17z"/></svg>
    </button>
    <div class="md-select__inner">
      <ul class="md-select__list">
        
          <li class="md-select__item">
            <a href="/" hreflang="" class="md-select__link">
              en - English
            </a>
          </li>
        
          <li class="md-select__item">
            <a href="/de/" hreflang="" class="md-select__link">
              de - Deutsch
            </a>
          </li>
        
          <li class="md-select__item">
            <a href="/es/" hreflang="" class="md-select__link">
              es - español
            </a>
          </li>
        
          <li class="md-select__item">
            <a href="/fr/" hreflang="" class="md-select__link">
              fr - français
            </a>
          </li>
        
          <li class="md-select__item">
            <a href="/hi/" hreflang="" class="md-select__link">
              hi - हिन्दी
            </a>
          </li>
        
          <li class="md-select__item">
            <a href="/ja/" hreflang="" class="md-select__link">
              ja - 日本語
            </a>
          </li>
        
          <li class="md-select__item">
            <a href="/ko/" hreflang="" class="md-select__link">
              ko - 한국어
            </a>
          </li>
        
          <li class="md-select__item">
            <a href="/pt/" hreflang="" class="md-select__link">
              pt - português
            </a>
          </li>
        
          <li class="md-select__item">
            <a href="/ru/" hreflang="" class="md-select__link">
              ru - русский язык
            </a>
          </li>
        
          <li class="md-select__item">
            <a href="/tr/" hreflang="" class="md-select__link">
              tr - Türkçe
            </a>
          </li>
        
          <li class="md-select__item">
            <a href="/uk/" hreflang="" class="md-select__link">
              uk - українська мова
            </a>
          </li>
        
          <li class="md-select__item">
            <a href="/zh/" hreflang="" class="md-select__link">
              zh - 简体中文
            </a>
          </li>
        
          <li class="md-select__item">
            <a href="/zh-hant/" hreflang="" class="md-select__link">
              zh-hant - 繁體中文
            </a>
          </li>
        
      </ul>
    </div>
  </div>
</div>
    
    
      
      
        <label class="md-header__button md-icon" for="__search" aria-label="Search">
          
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M9.5 3A6.5 6.5 0 0 1 16 9.5c0 1.61-.59 3.09-1.56 4.23l.27.27h.79l5 5-1.5 1.5-5-5v-.79l-.27-.27A6.52 6.52 0 0 1 9.5 16 6.5 6.5 0 0 1 3 9.5 6.5 6.5 0 0 1 9.5 3m0 2C7 5 5 7 5 9.5S7 14 9.5 14 14 12 14 9.5 12 5 9.5 5"/></svg>
        </label>
        <div class="md-search" data-md-component="search" role="dialog" aria-label="Search">
  <button type="button" class="md-search__button">
    Search
  </button>
</div>
      
    
    <div class="md-header__source">
      
        <a href="https://github.com/fastapi/fastapi" title="Go to repository" class="md-source" data-md-component="source">
  <div class="md-source__icon md-icon">
    
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M10.226 17.284c-2.965-.36-5.054-2.493-5.054-5.256 0-1.123.404-2.336 1.078-3.144-.292-.741-.247-2.314.09-2.965.898-.112 2.111.36 2.83 1.01.853-.269 1.752-.404 2.853-.404 1.1 0 1.999.135 2.807.382.696-.629 1.932-1.1 2.83-.988.315.606.36 2.179.067 2.942.72.854 1.101 2 1.101 3.167 0 2.763-2.089 4.852-5.098 5.234.763.494 1.28 1.572 1.28 2.807v2.336c0 .674.561 1.056 1.235.786 4.066-1.55 7.255-5.615 7.255-10.646C23.5 6.188 18.334 1 11.978 1 5.62 1 .5 6.188.5 12.545c0 4.986 3.167 9.12 7.435 10.669.606.225 1.19-.18 1.19-.786V20.63a2.9 2.9 0 0 1-1.078.224c-1.483 0-2.359-.808-2.987-2.313-.247-.607-.517-.966-1.034-1.033-.27-.023-.359-.135-.359-.27 0-.27.45-.471.898-.471.652 0 1.213.404 1.797 1.235.45.651.921.943 1.483.943.561 0 .92-.202 1.437-.719.382-.381.674-.718.944-.943"/></svg>
  </div>
  <div class="md-source__repository">
    fastapi/fastapi
  </div>
</a>
      
    </div>
  </nav>
  
    
      
<nav class="md-tabs" aria-label="Tabs" data-md-component="tabs">
  <div class="md-grid">
    <ul class="md-tabs__list">
      
        
  
  
  
  
    <li class="md-tabs__item">
      <a href="../.." class="md-tabs__link">
        
  
  FastAPI

      </a>
    </li>
  

      
        
  
  
  
  
    <li class="md-tabs__item">
      <a href="../../features/" class="md-tabs__link">
        
  
  Features

      </a>
    </li>
  

      
        
  
  
  
    
  
  
    
      
      
        
          
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
    
    
    
    
      <li class="md-tabs__item md-tabs__item--active">
        <a href="../../learn/" class="md-tabs__link">
          
  
  Learn

        </a>
      </li>
    
  

      
        
  
  
  
  
    
      
      
        
          
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
    
    
    
    
      <li class="md-tabs__item">
        <a href="../../reference/" class="md-tabs__link">
          
  
  Reference

        </a>
      </li>
    
  

      
        
  
  
  
  
    
      
      
        
          
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
    
    
    
    
      <li class="md-tabs__item">
        <a href="../../resources/" class="md-tabs__link">
          
  
  Resources

        </a>
      </li>
    
  

      
        
  
  
  
  
    
      
      
        
          
        
      
        
      
        
      
        
      
        
      
    
    
    
    
      <li class="md-tabs__item">
        <a href="../../about/" class="md-tabs__link">
          
  
  About

        </a>
      </li>
    
  

      
        
  
  
  
  
    <li class="md-tabs__item">
      <a href="../../release-notes/" class="md-tabs__link">
        
  
  Release Notes

      </a>
    </li>
  

      
    </ul>
  </div>
</nav>
    
  
</header>
    
    <div class="md-container" data-md-component="container">
      
      
        
      
      <main class="md-main" data-md-component="main">
        <div class="md-main__inner md-grid">
          
  
    
    <div class="md-sidebar md-sidebar--primary" data-md-component="sidebar" data-md-type="navigation" >
      <div class="md-sidebar__scrollwrap">
        <div class="md-sidebar__inner">
          


  


<nav class="md-nav md-nav--primary md-nav--lifted" aria-label="Navigation" data-md-level="0">
  <label class="md-nav__title" for="__drawer">
    <a href="../.." title="FastAPI" class="md-nav__button md-logo" aria-label="FastAPI" data-md-component="logo">
      
  <img src="../../img/icon-white.svg" alt="FastAPI">

    </a>
    FastAPI
  </label>
  
    <div class="md-nav__source">
      <a href="https://github.com/fastapi/fastapi" title="Go to repository" class="md-source" data-md-component="source">
  <div class="md-source__icon md-icon">
    
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M10.226 17.284c-2.965-.36-5.054-2.493-5.054-5.256 0-1.123.404-2.336 1.078-3.144-.292-.741-.247-2.314.09-2.965.898-.112 2.111.36 2.83 1.01.853-.269 1.752-.404 2.853-.404 1.1 0 1.999.135 2.807.382.696-.629 1.932-1.1 2.83-.988.315.606.36 2.179.067 2.942.72.854 1.101 2 1.101 3.167 0 2.763-2.089 4.852-5.098 5.234.763.494 1.28 1.572 1.28 2.807v2.336c0 .674.561 1.056 1.235.786 4.066-1.55 7.255-5.615 7.255-10.646C23.5 6.188 18.334 1 11.978 1 5.62 1 .5 6.188.5 12.545c0 4.986 3.167 9.12 7.435 10.669.606.225 1.19-.18 1.19-.786V20.63a2.9 2.9 0 0 1-1.078.224c-1.483 0-2.359-.808-2.987-2.313-.247-.607-.517-.966-1.034-1.033-.27-.023-.359-.135-.359-.27 0-.27.45-.471.898-.471.652 0 1.213.404 1.797 1.235.45.651.921.943 1.483.943.561 0 .92-.202 1.437-.719.382-.381.674-.718.944-.943"/></svg>
  </div>
  <div class="md-source__repository">
    fastapi/fastapi
  </div>
</a>
    </div>
  
  <ul class="md-nav__list" data-md-scrollfix>
    
      
      
  
  
  
  
    <li class="md-nav__item">
      <a href="../.." class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  FastAPI

    
  </span>
  
  

      </a>
    </li>
  

    
      
      
  
  
  
  
    <li class="md-nav__item">
      <a href="../../features/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Features

    
  </span>
  
  

      </a>
    </li>
  

    
      
      
  
  
    
  
  
  
    
    
      
        
          
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
    
    
    
      
        
        
      
      
    
    
    <li class="md-nav__item md-nav__item--active md-nav__item--section md-nav__item--nested">
      
        
        
        <input class="md-nav__toggle md-toggle " type="checkbox" id="__nav_3" checked>
        
          
          <div class="md-nav__link md-nav__container">
            <a href="../../learn/" class="md-nav__link ">
              
  
  
  <span class="md-ellipsis">
    
  
  Learn

    
  </span>
  
  

            </a>
            
              
              <label class="md-nav__link " for="__nav_3" id="__nav_3_label" tabindex="">
                <span class="md-nav__icon md-icon"></span>
              </label>
            
          </div>
        
        <nav class="md-nav" data-md-level="1" aria-labelledby="__nav_3_label" aria-expanded="true">
          <label class="md-nav__title" for="__nav_3">
            <span class="md-nav__icon md-icon"></span>
            
  
  

          </label>
          <ul class="md-nav__list" data-md-scrollfix>
            
              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../python-types/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Python Types Intro

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../async/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Concurrency and async / await

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    
    
      
        
          
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
    
    
    
      
      
    
    
    <li class="md-nav__item md-nav__item--nested">
      
        
        
        <input class="md-nav__toggle md-toggle " type="checkbox" id="__nav_3_4" >
        
          
          <div class="md-nav__link md-nav__container">
            <a href="../../tutorial/" class="md-nav__link ">
              
  
  
  <span class="md-ellipsis">
    
  
  Tutorial - User Guide

    
  </span>
  
  

            </a>
            
              
              <label class="md-nav__link " for="__nav_3_4" id="__nav_3_4_label" tabindex="0">
                <span class="md-nav__icon md-icon"></span>
              </label>
            
          </div>
        
        <nav class="md-nav" data-md-level="2" aria-labelledby="__nav_3_4_label" aria-expanded="false">
          <label class="md-nav__title" for="__nav_3_4">
            <span class="md-nav__icon md-icon"></span>
            
  
  

          </label>
          <ul class="md-nav__list" data-md-scrollfix>
            
              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/first-steps/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  First Steps

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/path-params/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Path Parameters

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/query-params/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Query Parameters

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/body/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Request Body

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/query-params-str-validations/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Query Parameters and String Validations

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/path-params-numeric-validations/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Path Parameters and Numeric Validations

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/query-param-models/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Query Parameter Models

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/body-multiple-params/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Body - Multiple Parameters

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/body-fields/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Body - Fields

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/body-nested-models/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Body - Nested Models

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/schema-extra-example/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Declare Request Example Data

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/extra-data-types/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Extra Data Types

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/cookie-params/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Cookie Parameters

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/header-params/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Header Parameters

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/cookie-param-models/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Cookie Parameter Models

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/header-param-models/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Header Parameter Models

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/response-model/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Response Model - Return Type

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/extra-models/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Extra Models

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/response-status-code/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Response Status Code

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/request-forms/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Form Data

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/request-form-models/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Form Models

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/request-files/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Request Files

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/request-forms-and-files/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Request Forms and Files

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/handling-errors/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Handling Errors

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/path-operation-configuration/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Path Operation Configuration

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/encoder/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  JSON Compatible Encoder

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/body-updates/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Body - Updates

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    
    
      
        
          
        
      
        
      
        
      
        
      
        
      
        
      
    
    
    
      
      
    
    
    <li class="md-nav__item md-nav__item--nested">
      
        
        
        <input class="md-nav__toggle md-toggle " type="checkbox" id="__nav_3_4_29" >
        
          
          <div class="md-nav__link md-nav__container">
            <a href="../../tutorial/dependencies/" class="md-nav__link ">
              
  
  
  <span class="md-ellipsis">
    
  
  Dependencies

    
  </span>
  
  

            </a>
            
              
              <label class="md-nav__link " for="__nav_3_4_29" id="__nav_3_4_29_label" tabindex="0">
                <span class="md-nav__icon md-icon"></span>
              </label>
            
          </div>
        
        <nav class="md-nav" data-md-level="3" aria-labelledby="__nav_3_4_29_label" aria-expanded="false">
          <label class="md-nav__title" for="__nav_3_4_29">
            <span class="md-nav__icon md-icon"></span>
            
  
  

          </label>
          <ul class="md-nav__list" data-md-scrollfix>
            
              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/dependencies/classes-as-dependencies/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Classes as Dependencies

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/dependencies/sub-dependencies/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Sub-dependencies

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/dependencies/dependencies-in-path-operation-decorators/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Dependencies in path operation decorators

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/dependencies/global-dependencies/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Global Dependencies

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/dependencies/dependencies-with-yield/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Dependencies with yield

    
  </span>
  
  

      </a>
    </li>
  

              
            
          </ul>
        </nav>
      
    </li>
  

              
            
              
                
  
  
  
  
    
    
      
        
          
        
      
        
      
        
      
        
      
        
      
    
    
    
      
      
    
    
    <li class="md-nav__item md-nav__item--nested">
      
        
        
        <input class="md-nav__toggle md-toggle " type="checkbox" id="__nav_3_4_30" >
        
          
          <div class="md-nav__link md-nav__container">
            <a href="../../tutorial/security/" class="md-nav__link ">
              
  
  
  <span class="md-ellipsis">
    
  
  Security

    
  </span>
  
  

            </a>
            
              
              <label class="md-nav__link " for="__nav_3_4_30" id="__nav_3_4_30_label" tabindex="0">
                <span class="md-nav__icon md-icon"></span>
              </label>
            
          </div>
        
        <nav class="md-nav" data-md-level="3" aria-labelledby="__nav_3_4_30_label" aria-expanded="false">
          <label class="md-nav__title" for="__nav_3_4_30">
            <span class="md-nav__icon md-icon"></span>
            
  
  

          </label>
          <ul class="md-nav__list" data-md-scrollfix>
            
              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/security/first-steps/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Security - First Steps

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/security/get-current-user/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Get Current User

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/security/simple-oauth2/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Simple OAuth2 with Password and Bearer

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/security/oauth2-jwt/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  OAuth2 with Password (and hashing), Bearer with JWT tokens

    
  </span>
  
  

      </a>
    </li>
  

              
            
          </ul>
        </nav>
      
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/middleware/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Middleware

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/cors/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  CORS (Cross-Origin Resource Sharing)

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/sql-databases/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  SQL (Relational) Databases

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/bigger-applications/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Bigger Applications - Multiple Files

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/stream-json-lines/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Stream JSON Lines

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/server-sent-events/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Server-Sent Events (SSE)

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/background-tasks/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Background Tasks

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/metadata/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Metadata and Docs URLs

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/frontend/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Frontend

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/static-files/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Static Files

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/testing/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Testing

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../tutorial/debugging/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Debugging

    
  </span>
  
  

      </a>
    </li>
  

              
            
          </ul>
        </nav>
      
    </li>
  

              
            
              
                
  
  
    
  
  
  
    
    
      
        
          
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
    
    
    
      
      
    
    
    <li class="md-nav__item md-nav__item--active md-nav__item--nested">
      
        
        
        <input class="md-nav__toggle md-toggle " type="checkbox" id="__nav_3_5" checked>
        
          
          <div class="md-nav__link md-nav__container">
            <a href="../" class="md-nav__link ">
              
  
  
  <span class="md-ellipsis">
    
  
  Advanced User Guide

    
  </span>
  
  

            </a>
            
              
              <label class="md-nav__link " for="__nav_3_5" id="__nav_3_5_label" tabindex="0">
                <span class="md-nav__icon md-icon"></span>
              </label>
            
          </div>
        
        <nav class="md-nav" data-md-level="2" aria-labelledby="__nav_3_5_label" aria-expanded="true">
          <label class="md-nav__title" for="__nav_3_5">
            <span class="md-nav__icon md-icon"></span>
            
  
  

          </label>
          <ul class="md-nav__list" data-md-scrollfix>
            
              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../stream-data/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Stream Data

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../path-operation-advanced-configuration/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Path Operation Advanced Configuration

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../additional-status-codes/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Additional Status Codes

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../response-directly/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Return a Response Directly

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
    
  
  
  
    <li class="md-nav__item md-nav__item--active">
      
      
        <input class="md-nav__toggle md-toggle" type="checkbox" id="__toc">
      
      
      
        
      
      
        <label class="md-nav__link md-nav__link--active" for="__toc">
          
  
  
  <span class="md-ellipsis">
    
  
  Custom Response - HTML, Stream, File, others

    
  </span>
  
  

          <span class="md-nav__icon md-icon"></span>
        </label>
      
      <a href="././" class="md-nav__link md-nav__link--active">
        
  
  
  <span class="md-ellipsis">
    
  
  Custom Response - HTML, Stream, File, others

    
  </span>
  
  

      </a>
      
        


<nav class="md-nav md-nav--secondary" aria-label="On this page">
  
  
  
    
  
  
    <label class="md-nav__title" for="__toc">
      <span class="md-nav__icon md-icon"></span>
      On this page
    </label>
    <ul class="md-nav__list" data-md-component="toc" data-md-scrollfix>
      
        <li class="md-nav__item">
  <a href="#json-responses" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        JSON Responses
      </span>
    </span>
  </a>
  
    <nav class="md-nav" aria-label="JSON Responses">
      <ul class="md-nav__list">
        
          <li class="md-nav__item">
  <a href="#json-performance" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        JSON Performance
      </span>
    </span>
  </a>
  
</li>
        
      </ul>
    </nav>
  
</li>
      
        <li class="md-nav__item">
  <a href="#html-response" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        HTML Response
      </span>
    </span>
  </a>
  
    <nav class="md-nav" aria-label="HTML Response">
      <ul class="md-nav__list">
        
          <li class="md-nav__item">
  <a href="#return-a-response" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Return a <code>Response</code>
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#document-in-openapi-and-override-response" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Document in OpenAPI and override <code>Response</code>
      </span>
    </span>
  </a>
  
    <nav class="md-nav" aria-label="Document in OpenAPI and override Response">
      <ul class="md-nav__list">
        
          <li class="md-nav__item">
  <a href="#return-an-htmlresponse-directly" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Return an <code>HTMLResponse</code> directly
      </span>
    </span>
  </a>
  
</li>
        
      </ul>
    </nav>
  
</li>
        
      </ul>
    </nav>
  
</li>
      
        <li class="md-nav__item">
  <a href="#available-responses" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Available responses
      </span>
    </span>
  </a>
  
    <nav class="md-nav" aria-label="Available responses">
      <ul class="md-nav__list">
        
          <li class="md-nav__item">
  <a href="#response" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        <code>Response</code>
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#htmlresponse" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        <code>HTMLResponse</code>
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#plaintextresponse" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        <code>PlainTextResponse</code>
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#jsonresponse" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        <code>JSONResponse</code>
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#redirectresponse" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        <code>RedirectResponse</code>
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#streamingresponse" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        <code>StreamingResponse</code>
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#fileresponse" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        <code>FileResponse</code>
      </span>
    </span>
  </a>
  
</li>
        
      </ul>
    </nav>
  
</li>
      
        <li class="md-nav__item">
  <a href="#custom-response-class" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Custom response class
      </span>
    </span>
  </a>
  
    <nav class="md-nav" aria-label="Custom response class">
      <ul class="md-nav__list">
        
          <li class="md-nav__item">
  <a href="#orjson-or-response-model" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        <code>orjson</code> or Response Model
      </span>
    </span>
  </a>
  
</li>
        
      </ul>
    </nav>
  
</li>
      
        <li class="md-nav__item">
  <a href="#default-response-class" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Default response class
      </span>
    </span>
  </a>
  
</li>
      
        <li class="md-nav__item">
  <a href="#additional-documentation" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Additional documentation
      </span>
    </span>
  </a>
  
</li>
      
    </ul>
  
</nav>
      
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../additional-responses/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Additional Responses in OpenAPI

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../response-cookies/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Response Cookies

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../response-headers/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Response Headers

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../response-change-status-code/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Response - Change Status Code

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../advanced-dependencies/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Advanced Dependencies

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    
    
      
        
          
        
      
        
      
        
      
    
    
    
      
      
    
    
    <li class="md-nav__item md-nav__item--nested">
      
        
        
        <input class="md-nav__toggle md-toggle " type="checkbox" id="__nav_3_5_12" >
        
          
          <div class="md-nav__link md-nav__container">
            <a href="../security/" class="md-nav__link ">
              
  
  
  <span class="md-ellipsis">
    
  
  Advanced Security

    
  </span>
  
  

            </a>
            
              
              <label class="md-nav__link " for="__nav_3_5_12" id="__nav_3_5_12_label" tabindex="0">
                <span class="md-nav__icon md-icon"></span>
              </label>
            
          </div>
        
        <nav class="md-nav" data-md-level="3" aria-labelledby="__nav_3_5_12_label" aria-expanded="false">
          <label class="md-nav__title" for="__nav_3_5_12">
            <span class="md-nav__icon md-icon"></span>
            
  
  

          </label>
          <ul class="md-nav__list" data-md-scrollfix>
            
              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../security/oauth2-scopes/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  OAuth2 scopes

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../security/http-basic-auth/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  HTTP Basic Auth

    
  </span>
  
  

      </a>
    </li>
  

              
            
          </ul>
        </nav>
      
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../using-request-directly/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Using the Request Directly

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../dataclasses/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Using Dataclasses

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../middleware/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Advanced Middleware

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../sub-applications/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Sub Applications - Mounts

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../behind-a-proxy/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Behind a Proxy

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../templates/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Templates

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../websockets/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  WebSockets

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../events/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Lifespan Events

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../testing-websockets/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Testing WebSockets

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../testing-events/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Testing Events: lifespan and startup - shutdown

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../testing-dependencies/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Testing Dependencies with Overrides

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../async-tests/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Async Tests

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../settings/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Settings and Environment Variables

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../openapi-callbacks/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  OpenAPI Callbacks

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../openapi-webhooks/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  OpenAPI Webhooks

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../wsgi/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Including WSGI - Flask, Django, others

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../generate-clients/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Generating SDKs

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../advanced-python-types/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Advanced Python Types

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../json-base64-bytes/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  JSON with Bytes as Base64

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../strict-content-type/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Strict Content-Type Checking

    
  </span>
  
  

      </a>
    </li>
  

              
            
          </ul>
        </nav>
      
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../fastapi-cli/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  FastAPI CLI

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../editor-support/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Editor Support

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    
    
      
        
          
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
    
    
    
      
      
    
    
    <li class="md-nav__item md-nav__item--nested">
      
        
        
        <input class="md-nav__toggle md-toggle " type="checkbox" id="__nav_3_8" >
        
          
          <div class="md-nav__link md-nav__container">
            <a href="../../deployment/" class="md-nav__link ">
              
  
  
  <span class="md-ellipsis">
    
  
  Deployment

    
  </span>
  
  

            </a>
            
              
              <label class="md-nav__link " for="__nav_3_8" id="__nav_3_8_label" tabindex="0">
                <span class="md-nav__icon md-icon"></span>
              </label>
            
          </div>
        
        <nav class="md-nav" data-md-level="2" aria-labelledby="__nav_3_8_label" aria-expanded="false">
          <label class="md-nav__title" for="__nav_3_8">
            <span class="md-nav__icon md-icon"></span>
            
  
  

          </label>
          <ul class="md-nav__list" data-md-scrollfix>
            
              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../deployment/versions/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  About FastAPI versions

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../deployment/fastapicloud/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  FastAPI Cloud

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../deployment/https/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  About HTTPS

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../deployment/manually/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Run a Server Manually

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../deployment/concepts/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Deployments Concepts

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../deployment/cloud/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Deploy FastAPI on Cloud Providers

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../deployment/server-workers/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Server Workers - Uvicorn with Workers

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../deployment/docker/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  FastAPI in Containers - Docker

    
  </span>
  
  

      </a>
    </li>
  

              
            
          </ul>
        </nav>
      
    </li>
  

              
            
              
                
  
  
  
  
    
    
      
        
          
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
    
    
    
      
      
    
    
    <li class="md-nav__item md-nav__item--nested">
      
        
        
        <input class="md-nav__toggle md-toggle " type="checkbox" id="__nav_3_9" >
        
          
          <div class="md-nav__link md-nav__container">
            <a href="../../how-to/" class="md-nav__link ">
              
  
  
  <span class="md-ellipsis">
    
  
  How To - Recipes

    
  </span>
  
  

            </a>
            
              
              <label class="md-nav__link " for="__nav_3_9" id="__nav_3_9_label" tabindex="0">
                <span class="md-nav__icon md-icon"></span>
              </label>
            
          </div>
        
        <nav class="md-nav" data-md-level="2" aria-labelledby="__nav_3_9_label" aria-expanded="false">
          <label class="md-nav__title" for="__nav_3_9">
            <span class="md-nav__icon md-icon"></span>
            
  
  

          </label>
          <ul class="md-nav__list" data-md-scrollfix>
            
              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../how-to/general/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  General - How To - Recipes

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../how-to/migrate-from-pydantic-v1-to-pydantic-v2/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Migrate from Pydantic v1 to Pydantic v2

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../how-to/graphql/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  GraphQL

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../how-to/custom-request-and-route/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Custom Request and APIRoute class

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../how-to/conditional-openapi/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Conditional OpenAPI

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../how-to/extending-openapi/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Extending OpenAPI

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../how-to/separate-openapi-schemas/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Separate OpenAPI Schemas for Input and Output or Not

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../how-to/custom-docs-ui-assets/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Custom Docs UI Static Assets (Self-Hosting)

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../how-to/configure-swagger-ui/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Configure Swagger UI

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../how-to/testing-database/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Testing a Database

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../how-to/authentication-error-status-code/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Use Old 403 Authentication Error Status Codes

    
  </span>
  
  

      </a>
    </li>
  

              
            
          </ul>
        </nav>
      
    </li>
  

              
            
          </ul>
        </nav>
      
    </li>
  

    
      
      
  
  
  
  
    
    
      
        
          
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
    
    
    
      
      
    
    
    <li class="md-nav__item md-nav__item--nested">
      
        
        
        <input class="md-nav__toggle md-toggle " type="checkbox" id="__nav_4" >
        
          
          <div class="md-nav__link md-nav__container">
            <a href="../../reference/" class="md-nav__link ">
              
  
  
  <span class="md-ellipsis">
    
  
  Reference

    
  </span>
  
  

            </a>
            
              
              <label class="md-nav__link " for="__nav_4" id="__nav_4_label" tabindex="0">
                <span class="md-nav__icon md-icon"></span>
              </label>
            
          </div>
        
        <nav class="md-nav" data-md-level="1" aria-labelledby="__nav_4_label" aria-expanded="false">
          <label class="md-nav__title" for="__nav_4">
            <span class="md-nav__icon md-icon"></span>
            
  
  

          </label>
          <ul class="md-nav__list" data-md-scrollfix>
            
              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/fastapi/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  FastAPI class

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/parameters/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Request Parameters

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/status/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Status Codes

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/uploadfile/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  UploadFile class

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/exceptions/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Exceptions - HTTPException and WebSocketException

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/dependencies/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Dependencies - Depends() and Security()

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/apirouter/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  APIRouter class

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/background/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Background Tasks - BackgroundTasks

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/request/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Request class

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/websockets/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  WebSockets

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/httpconnection/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  HTTPConnection class

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/response/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Response class

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/responses/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Custom Response Classes - File, HTML, Redirect, Streaming, etc.

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/sse/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Server-Sent Events - EventSourceResponse and ServerSentEvent

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/middleware/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Middleware

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    
    
      
        
          
        
      
        
      
        
      
    
    
    
      
      
    
    
    <li class="md-nav__item md-nav__item--nested">
      
        
        
        <input class="md-nav__toggle md-toggle " type="checkbox" id="__nav_4_17" >
        
          
          <div class="md-nav__link md-nav__container">
            <a href="../../reference/openapi/" class="md-nav__link ">
              
  
  
  <span class="md-ellipsis">
    
  
  OpenAPI

    
  </span>
  
  

            </a>
            
              
              <label class="md-nav__link " for="__nav_4_17" id="__nav_4_17_label" tabindex="0">
                <span class="md-nav__icon md-icon"></span>
              </label>
            
          </div>
        
        <nav class="md-nav" data-md-level="2" aria-labelledby="__nav_4_17_label" aria-expanded="false">
          <label class="md-nav__title" for="__nav_4_17">
            <span class="md-nav__icon md-icon"></span>
            
  
  

          </label>
          <ul class="md-nav__list" data-md-scrollfix>
            
              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/openapi/docs/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  OpenAPI docs

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/openapi/models/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  OpenAPI models

    
  </span>
  
  

      </a>
    </li>
  

              
            
          </ul>
        </nav>
      
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/security/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Security Tools

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/encoders/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Encoders - jsonable_encoder

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/staticfiles/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Static Files - StaticFiles

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/templating/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Templating - Jinja2Templates

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../reference/testclient/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Test Client - TestClient

    
  </span>
  
  

      </a>
    </li>
  

              
            
          </ul>
        </nav>
      
    </li>
  

    
      
      
  
  
  
  
    
    
      
        
          
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
    
    
    
      
      
    
    
    <li class="md-nav__item md-nav__item--nested">
      
        
        
        <input class="md-nav__toggle md-toggle " type="checkbox" id="__nav_5" >
        
          
          <div class="md-nav__link md-nav__container">
            <a href="../../resources/" class="md-nav__link ">
              
  
  
  <span class="md-ellipsis">
    
  
  Resources

    
  </span>
  
  

            </a>
            
              
              <label class="md-nav__link " for="__nav_5" id="__nav_5_label" tabindex="0">
                <span class="md-nav__icon md-icon"></span>
              </label>
            
          </div>
        
        <nav class="md-nav" data-md-level="1" aria-labelledby="__nav_5_label" aria-expanded="false">
          <label class="md-nav__title" for="__nav_5">
            <span class="md-nav__icon md-icon"></span>
            
  
  

          </label>
          <ul class="md-nav__list" data-md-scrollfix>
            
              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../fastapi-people/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  FastAPI People

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../help-fastapi/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Help

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../contributing/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Contributing

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../translations/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Translations

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../project-generation/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Full Stack FastAPI Template

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../external-links/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  External Links

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../newsletter/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  FastAPI and friends newsletter

    
  </span>
  
  

      </a>
    </li>
  

              
            
          </ul>
        </nav>
      
    </li>
  

    
      
      
  
  
  
  
    
    
      
        
          
        
      
        
      
        
      
        
      
        
      
    
    
    
      
      
    
    
    <li class="md-nav__item md-nav__item--nested">
      
        
        
        <input class="md-nav__toggle md-toggle " type="checkbox" id="__nav_6" >
        
          
          <div class="md-nav__link md-nav__container">
            <a href="../../about/" class="md-nav__link ">
              
  
  
  <span class="md-ellipsis">
    
  
  About

    
  </span>
  
  

            </a>
            
              
              <label class="md-nav__link " for="__nav_6" id="__nav_6_label" tabindex="0">
                <span class="md-nav__icon md-icon"></span>
              </label>
            
          </div>
        
        <nav class="md-nav" data-md-level="1" aria-labelledby="__nav_6_label" aria-expanded="false">
          <label class="md-nav__title" for="__nav_6">
            <span class="md-nav__icon md-icon"></span>
            
  
  

          </label>
          <ul class="md-nav__list" data-md-scrollfix>
            
              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../alternatives/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Alternatives, Inspiration and Comparisons

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../history-design-future/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  History, Design and Future

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../benchmarks/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Benchmarks

    
  </span>
  
  

      </a>
    </li>
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../../management/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Repository Management

    
  </span>
  
  

      </a>
    </li>
  

              
            
          </ul>
        </nav>
      
    </li>
  

    
      
      
  
  
  
  
    <li class="md-nav__item">
      <a href="../../release-notes/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Release Notes

    
  </span>
  
  

      </a>
    </li>
  

    
  </ul>
</nav>
          
          
        </div>
      </div>
    </div>
  
  
    
    <div class="md-sidebar md-sidebar--secondary" data-md-component="sidebar" data-md-type="toc" >
      <div class="md-sidebar__scrollwrap">
        
        <div class="md-sidebar__inner">
          


<nav class="md-nav md-nav--secondary" aria-label="On this page">
  
  
  
    
  
  
    <label class="md-nav__title" for="__toc">
      <span class="md-nav__icon md-icon"></span>
      On this page
    </label>
    <ul class="md-nav__list" data-md-component="toc" data-md-scrollfix>
      
        <li class="md-nav__item">
  <a href="#json-responses" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        JSON Responses
      </span>
    </span>
  </a>
  
    <nav class="md-nav" aria-label="JSON Responses">
      <ul class="md-nav__list">
        
          <li class="md-nav__item">
  <a href="#json-performance" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        JSON Performance
      </span>
    </span>
  </a>
  
</li>
        
      </ul>
    </nav>
  
</li>
      
        <li class="md-nav__item">
  <a href="#html-response" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        HTML Response
      </span>
    </span>
  </a>
  
    <nav class="md-nav" aria-label="HTML Response">
      <ul class="md-nav__list">
        
          <li class="md-nav__item">
  <a href="#return-a-response" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Return a <code>Response</code>
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#document-in-openapi-and-override-response" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Document in OpenAPI and override <code>Response</code>
      </span>
    </span>
  </a>
  
    <nav class="md-nav" aria-label="Document in OpenAPI and override Response">
      <ul class="md-nav__list">
        
          <li class="md-nav__item">
  <a href="#return-an-htmlresponse-directly" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Return an <code>HTMLResponse</code> directly
      </span>
    </span>
  </a>
  
</li>
        
      </ul>
    </nav>
  
</li>
        
      </ul>
    </nav>
  
</li>
      
        <li class="md-nav__item">
  <a href="#available-responses" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Available responses
      </span>
    </span>
  </a>
  
    <nav class="md-nav" aria-label="Available responses">
      <ul class="md-nav__list">
        
          <li class="md-nav__item">
  <a href="#response" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        <code>Response</code>
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#htmlresponse" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        <code>HTMLResponse</code>
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#plaintextresponse" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        <code>PlainTextResponse</code>
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#jsonresponse" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        <code>JSONResponse</code>
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#redirectresponse" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        <code>RedirectResponse</code>
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#streamingresponse" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        <code>StreamingResponse</code>
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#fileresponse" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        <code>FileResponse</code>
      </span>
    </span>
  </a>
  
</li>
        
      </ul>
    </nav>
  
</li>
      
        <li class="md-nav__item">
  <a href="#custom-response-class" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Custom response class
      </span>
    </span>
  </a>
  
    <nav class="md-nav" aria-label="Custom response class">
      <ul class="md-nav__list">
        
          <li class="md-nav__item">
  <a href="#orjson-or-response-model" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        <code>orjson</code> or Response Model
      </span>
    </span>
  </a>
  
</li>
        
      </ul>
    </nav>
  
</li>
      
        <li class="md-nav__item">
  <a href="#default-response-class" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Default response class
      </span>
    </span>
  </a>
  
</li>
      
        <li class="md-nav__item">
  <a href="#additional-documentation" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Additional documentation
      </span>
    </span>
  </a>
  
</li>
      
    </ul>
  
</nav>
        </div>
      </div>
    </div>
  

          
            <div class="md-content" data-md-component="content">
              
                



  


  <nav class="md-path" aria-label="Navigation" >
    <ol class="md-path__list">
      
        
  
  
    <li class="md-path__item">
      <a href="../.." class="md-path__link">
        
  
  <span class="md-ellipsis">
    FastAPI
  </span>

      </a>
    </li>
  

      
      
        
  
  
    
    
      
        
          
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
    
    
    
    
      <li class="md-path__item">
        <a href="../../learn/" class="md-path__link">
          
  
  <span class="md-ellipsis">
    Learn
  </span>

        </a>
      </li>
    
  

      
        
  
  
    
    
      
        
          
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
    
    
    
    
      <li class="md-path__item">
        <a href="../" class="md-path__link">
          
  
  <span class="md-ellipsis">
    Advanced User Guide
  </span>

        </a>
      </li>
    
  

      
    </ol>
  </nav>

              
              <article class="md-content__inner md-typeset">
                
  
  
  
  


<h1 id="custom-response-html-stream-file-others">Custom Response - HTML, Stream, File, others<a class="headerlink" href="#custom-response-html-stream-file-others" title="Permanent link">&para;</a></h1>
<p>By default, <strong>FastAPI</strong> will return JSON responses.</p>
<p>You can override it by returning a <code>Response</code> directly as seen in <a href="../response-directly/">Return a Response directly</a>.</p>
<p>But if you return a <code>Response</code> directly (or any subclass, like <code>JSONResponse</code>), the data won't be automatically converted (even if you declare a <code>response_model</code>), and the documentation won't be automatically generated (for example, including the specific "media type", in the HTTP header <code>Content-Type</code> as part of the generated OpenAPI).</p>
<p>But you can also declare the <code>Response</code> that you want to be used (e.g. any <code>Response</code> subclass), in the <em>path operation decorator</em> using the <code>response_class</code> parameter.</p>
<p>The contents that you return from your <em>path operation function</em> will be put inside of that <code>Response</code>.</p>
<div class="admonition note">
<p class="admonition-title">Note</p>
<p>If you use a response class with no media type, FastAPI will expect your response to have no content, so it will not document the response format in its generated OpenAPI docs.</p>
</div>
<h2 id="json-responses">JSON Responses<a class="headerlink" href="#json-responses" title="Permanent link">&para;</a></h2>
<p>By default FastAPI returns JSON responses.</p>
<p>If you declare a <a href="../../tutorial/response-model/">Response Model</a> FastAPI will use it to serialize the data to JSON, using Pydantic.</p>
<p>If you don't declare a response model, FastAPI will use the <code>jsonable_encoder</code> explained in <a href="../../tutorial/encoder/">JSON Compatible Encoder</a> and put it in a <code>JSONResponse</code>.</p>
<p>If you declare a <code>response_class</code> with a JSON media type (<code>application/json</code>), like is the case with the <code>JSONResponse</code>, the data you return will be automatically converted (and filtered) with any Pydantic <code>response_model</code> that you declared in the <em>path operation decorator</em>. But the data won't be serialized to JSON bytes with Pydantic, instead it will be converted with the <code>jsonable_encoder</code> and then passed to the <code>JSONResponse</code> class, which will serialize it to bytes using the standard JSON library in Python.</p>
<h3 id="json-performance">JSON Performance<a class="headerlink" href="#json-performance" title="Permanent link">&para;</a></h3>
<p>In short, if you want the maximum performance, use a <a href="../../tutorial/response-model/">Response Model</a> and don't declare a <code>response_class</code> in the <em>path operation decorator</em>.</p>
<div class="tabbed-set tabbed-alternate" data-tabs="1:1"><input checked="checked" id="__tabbed_1_1" name="__tabbed_1" type="radio" /><div class="tabbed-labels"><label for="__tabbed_1_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-0-1"><span class="c1"># Code above omitted 👆</span>
</span><span id="__span-0-2">
</span><span id="__span-0-3"><span class="nd">@app</span><span class="o">.</span><span class="n">post</span><span class="p">(</span><span class="s2">&quot;/items/&quot;</span><span class="p">)</span>
</span><span id="__span-0-4"><span class="hll"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">create_item</span><span class="p">(</span><span class="n">item</span><span class="p">:</span> <span class="n">Item</span><span class="p">)</span> <span class="o">-&gt;</span> <span class="n">Item</span><span class="p">:</span>
</span></span><span id="__span-0-5">    <span class="k">return</span> <span class="n">item</span>
</span><span id="__span-0-6">
</span><span id="__span-0-7"><span class="c1"># Code below omitted 👇</span>
</span></code></pre></div>
</div>
</div>
</div>
<details>
<summary>👀 Full file preview</summary>
<div class="tabbed-set tabbed-alternate" data-tabs="2:1"><input checked="checked" id="__tabbed_2_1" name="__tabbed_2" type="radio" /><div class="tabbed-labels"><label for="__tabbed_2_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-1-1"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-1-2"><span class="kn">from</span><span class="w"> </span><span class="nn">pydantic</span><span class="w"> </span><span class="kn">import</span> <span class="n">BaseModel</span>
</span><span id="__span-1-3">
</span><span id="__span-1-4"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-1-5">
</span><span id="__span-1-6">
</span><span id="__span-1-7"><span class="k">class</span><span class="w"> </span><span class="nc">Item</span><span class="p">(</span><span class="n">BaseModel</span><span class="p">):</span>
</span><span id="__span-1-8">    <span class="n">name</span><span class="p">:</span> <span class="nb">str</span>
</span><span id="__span-1-9">    <span class="n">description</span><span class="p">:</span> <span class="nb">str</span> <span class="o">|</span> <span class="kc">None</span> <span class="o">=</span> <span class="kc">None</span>
</span><span id="__span-1-10">    <span class="n">price</span><span class="p">:</span> <span class="nb">float</span>
</span><span id="__span-1-11">    <span class="n">tax</span><span class="p">:</span> <span class="nb">float</span> <span class="o">|</span> <span class="kc">None</span> <span class="o">=</span> <span class="kc">None</span>
</span><span id="__span-1-12">    <span class="n">tags</span><span class="p">:</span> <span class="nb">list</span><span class="p">[</span><span class="nb">str</span><span class="p">]</span> <span class="o">=</span> <span class="p">[]</span>
</span><span id="__span-1-13">
</span><span id="__span-1-14">
</span><span id="__span-1-15"><span class="nd">@app</span><span class="o">.</span><span class="n">post</span><span class="p">(</span><span class="s2">&quot;/items/&quot;</span><span class="p">)</span>
</span><span id="__span-1-16"><span class="hll"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">create_item</span><span class="p">(</span><span class="n">item</span><span class="p">:</span> <span class="n">Item</span><span class="p">)</span> <span class="o">-&gt;</span> <span class="n">Item</span><span class="p">:</span>
</span></span><span id="__span-1-17">    <span class="k">return</span> <span class="n">item</span>
</span><span id="__span-1-18">
</span><span id="__span-1-19">
</span><span id="__span-1-20"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/items/&quot;</span><span class="p">)</span>
</span><span id="__span-1-21"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">read_items</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="nb">list</span><span class="p">[</span><span class="n">Item</span><span class="p">]:</span>
</span><span id="__span-1-22">    <span class="k">return</span> <span class="p">[</span>
</span><span id="__span-1-23">        <span class="n">Item</span><span class="p">(</span><span class="n">name</span><span class="o">=</span><span class="s2">&quot;Portal Gun&quot;</span><span class="p">,</span> <span class="n">price</span><span class="o">=</span><span class="mf">42.0</span><span class="p">),</span>
</span><span id="__span-1-24">        <span class="n">Item</span><span class="p">(</span><span class="n">name</span><span class="o">=</span><span class="s2">&quot;Plumbus&quot;</span><span class="p">,</span> <span class="n">price</span><span class="o">=</span><span class="mf">32.0</span><span class="p">),</span>
</span><span id="__span-1-25">    <span class="p">]</span>
</span></code></pre></div>
</div>
</div>
</div>
</details>
<h2 id="html-response">HTML Response<a class="headerlink" href="#html-response" title="Permanent link">&para;</a></h2>
<p>To return a response with HTML directly from <strong>FastAPI</strong>, use <code>HTMLResponse</code>.</p>
<ul>
<li>Import <code>HTMLResponse</code>.</li>
<li>Pass <code>HTMLResponse</code> as the parameter <code>response_class</code> of your <em>path operation decorator</em>.</li>
</ul>
<div class="tabbed-set tabbed-alternate" data-tabs="3:1"><input checked="checked" id="__tabbed_3_1" name="__tabbed_3" type="radio" /><div class="tabbed-labels"><label for="__tabbed_3_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-2-1"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-2-2"><span class="hll"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">HTMLResponse</span>
</span></span><span id="__span-2-3">
</span><span id="__span-2-4"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-2-5">
</span><span id="__span-2-6">
</span><span id="__span-2-7"><span class="hll"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/items/&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">HTMLResponse</span><span class="p">)</span>
</span></span><span id="__span-2-8"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">read_items</span><span class="p">():</span>
</span><span id="__span-2-9">    <span class="k">return</span> <span class="s2">&quot;&quot;&quot;</span>
</span><span id="__span-2-10"><span class="s2">    &lt;html&gt;</span>
</span><span id="__span-2-11"><span class="s2">        &lt;head&gt;</span>
</span><span id="__span-2-12"><span class="s2">            &lt;title&gt;Some HTML in here&lt;/title&gt;</span>
</span><span id="__span-2-13"><span class="s2">        &lt;/head&gt;</span>
</span><span id="__span-2-14"><span class="s2">        &lt;body&gt;</span>
</span><span id="__span-2-15"><span class="s2">            &lt;h1&gt;Look ma! HTML!&lt;/h1&gt;</span>
</span><span id="__span-2-16"><span class="s2">        &lt;/body&gt;</span>
</span><span id="__span-2-17"><span class="s2">    &lt;/html&gt;</span>
</span><span id="__span-2-18"><span class="s2">    &quot;&quot;&quot;</span>
</span></code></pre></div>
</div>
</div>
</div>
<div class="admonition note">
<p class="admonition-title">Note</p>
<p>The parameter <code>response_class</code> will also be used to define the "media type" of the response.</p>
<p>In this case, the HTTP header <code>Content-Type</code> will be set to <code>text/html</code>.</p>
<p>And it will be documented as such in OpenAPI.</p>
</div>
<h3 id="return-a-response">Return a <code>Response</code><a class="headerlink" href="#return-a-response" title="Permanent link">&para;</a></h3>
<p>As seen in <a href="../response-directly/">Return a Response directly</a>, you can also override the response directly in your <em>path operation</em>, by returning it.</p>
<p>The same example from above, returning an <code>HTMLResponse</code>, could look like:</p>
<div class="tabbed-set tabbed-alternate" data-tabs="4:1"><input checked="checked" id="__tabbed_4_1" name="__tabbed_4" type="radio" /><div class="tabbed-labels"><label for="__tabbed_4_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-3-1"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-3-2"><span class="hll"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">HTMLResponse</span>
</span></span><span id="__span-3-3">
</span><span id="__span-3-4"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-3-5">
</span><span id="__span-3-6">
</span><span id="__span-3-7"><span class="hll"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/items/&quot;</span><span class="p">)</span>
</span></span><span id="__span-3-8"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">read_items</span><span class="p">():</span>
</span><span id="__span-3-9">    <span class="n">html_content</span> <span class="o">=</span> <span class="s2">&quot;&quot;&quot;</span>
</span><span id="__span-3-10"><span class="s2">    &lt;html&gt;</span>
</span><span id="__span-3-11"><span class="s2">        &lt;head&gt;</span>
</span><span id="__span-3-12"><span class="s2">            &lt;title&gt;Some HTML in here&lt;/title&gt;</span>
</span><span id="__span-3-13"><span class="s2">        &lt;/head&gt;</span>
</span><span id="__span-3-14"><span class="s2">        &lt;body&gt;</span>
</span><span id="__span-3-15"><span class="s2">            &lt;h1&gt;Look ma! HTML!&lt;/h1&gt;</span>
</span><span id="__span-3-16"><span class="s2">        &lt;/body&gt;</span>
</span><span id="__span-3-17"><span class="s2">    &lt;/html&gt;</span>
</span><span id="__span-3-18"><span class="s2">    &quot;&quot;&quot;</span>
</span><span id="__span-3-19"><span class="hll">    <span class="k">return</span> <span class="n">HTMLResponse</span><span class="p">(</span><span class="n">content</span><span class="o">=</span><span class="n">html_content</span><span class="p">,</span> <span class="n">status_code</span><span class="o">=</span><span class="mi">200</span><span class="p">)</span>
</span></span></code></pre></div>
</div>
</div>
</div>
<div class="admonition warning">
<p class="admonition-title">Warning</p>
<p>A <code>Response</code> returned directly by your <em>path operation function</em> won't be documented in OpenAPI (for example, the <code>Content-Type</code> won't be documented) and won't be visible in the automatic interactive docs.</p>
</div>
<div class="admonition note">
<p class="admonition-title">Note</p>
<p>Of course, the actual <code>Content-Type</code> header, status code, etc, will come from the <code>Response</code> object you returned.</p>
</div>
<h3 id="document-in-openapi-and-override-response">Document in OpenAPI and override <code>Response</code><a class="headerlink" href="#document-in-openapi-and-override-response" title="Permanent link">&para;</a></h3>
<p>If you want to override the response from inside of the function but at the same time document the "media type" in OpenAPI, you can use the <code>response_class</code> parameter AND return a <code>Response</code> object.</p>
<p>The <code>response_class</code> will then be used only to document the OpenAPI <em>path operation</em>, but your <code>Response</code> will be used as is.</p>
<h4 id="return-an-htmlresponse-directly">Return an <code>HTMLResponse</code> directly<a class="headerlink" href="#return-an-htmlresponse-directly" title="Permanent link">&para;</a></h4>
<p>For example, it could be something like:</p>
<div class="tabbed-set tabbed-alternate" data-tabs="5:1"><input checked="checked" id="__tabbed_5_1" name="__tabbed_5" type="radio" /><div class="tabbed-labels"><label for="__tabbed_5_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-4-1"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-4-2"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">HTMLResponse</span>
</span><span id="__span-4-3">
</span><span id="__span-4-4"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-4-5">
</span><span id="__span-4-6">
</span><span id="__span-4-7"><span class="hll"><span class="k">def</span><span class="w"> </span><span class="nf">generate_html_response</span><span class="p">():</span>
</span></span><span id="__span-4-8">    <span class="n">html_content</span> <span class="o">=</span> <span class="s2">&quot;&quot;&quot;</span>
</span><span id="__span-4-9"><span class="s2">    &lt;html&gt;</span>
</span><span id="__span-4-10"><span class="s2">        &lt;head&gt;</span>
</span><span id="__span-4-11"><span class="s2">            &lt;title&gt;Some HTML in here&lt;/title&gt;</span>
</span><span id="__span-4-12"><span class="s2">        &lt;/head&gt;</span>
</span><span id="__span-4-13"><span class="s2">        &lt;body&gt;</span>
</span><span id="__span-4-14"><span class="s2">            &lt;h1&gt;Look ma! HTML!&lt;/h1&gt;</span>
</span><span id="__span-4-15"><span class="s2">        &lt;/body&gt;</span>
</span><span id="__span-4-16"><span class="s2">    &lt;/html&gt;</span>
</span><span id="__span-4-17"><span class="s2">    &quot;&quot;&quot;</span>
</span><span id="__span-4-18">    <span class="k">return</span> <span class="n">HTMLResponse</span><span class="p">(</span><span class="n">content</span><span class="o">=</span><span class="n">html_content</span><span class="p">,</span> <span class="n">status_code</span><span class="o">=</span><span class="mi">200</span><span class="p">)</span>
</span><span id="__span-4-19">
</span><span id="__span-4-20">
</span><span id="__span-4-21"><span class="hll"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/items/&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">HTMLResponse</span><span class="p">)</span>
</span></span><span id="__span-4-22"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">read_items</span><span class="p">():</span>
</span><span id="__span-4-23"><span class="hll">    <span class="k">return</span> <span class="n">generate_html_response</span><span class="p">()</span>
</span></span></code></pre></div>
</div>
</div>
</div>
<p>In this example, the function <code>generate_html_response()</code> already generates and returns a <code>Response</code> instead of returning the HTML in a <code>str</code>.</p>
<p>By returning the result of calling <code>generate_html_response()</code>, you are already returning a <code>Response</code> that will override the default <strong>FastAPI</strong> behavior.</p>
<p>But as you passed the <code>HTMLResponse</code> in the <code>response_class</code> too, <strong>FastAPI</strong> will know how to document it in OpenAPI and the interactive docs as HTML with <code>text/html</code>:</p>
<p><img src="/img/tutorial/custom-response/image01.png"></p>
<h2 id="available-responses">Available responses<a class="headerlink" href="#available-responses" title="Permanent link">&para;</a></h2>
<p>Here are some of the available responses.</p>
<p>Keep in mind that you can use <code>Response</code> to return anything else, or even create a custom sub-class.</p>
<div class="admonition note">
<p class="admonition-title">Technical Details</p>
<p>You could also use <code>from starlette.responses import HTMLResponse</code>.</p>
<p><strong>FastAPI</strong> provides the same <code>starlette.responses</code> as <code>fastapi.responses</code> just as a convenience for you, the developer. But most of the available responses come directly from Starlette.</p>
</div>
<h3 id="response"><code>Response</code><a class="headerlink" href="#response" title="Permanent link">&para;</a></h3>
<p>The main <code>Response</code> class, all the other responses inherit from it.</p>
<p>You can return it directly.</p>
<p>It accepts the following parameters:</p>
<ul>
<li><code>content</code> - A <code>str</code> or <code>bytes</code>.</li>
<li><code>status_code</code> - An <code>int</code> HTTP status code.</li>
<li><code>headers</code> - A <code>dict</code> of strings.</li>
<li><code>media_type</code> - A <code>str</code> giving the media type. E.g. <code>"text/html"</code>.</li>
</ul>
<p>FastAPI (actually Starlette) will automatically include a Content-Length header. It will also include a Content-Type header, based on the <code>media_type</code> and appending a charset for text types.</p>
<div class="tabbed-set tabbed-alternate" data-tabs="6:1"><input checked="checked" id="__tabbed_6_1" name="__tabbed_6" type="radio" /><div class="tabbed-labels"><label for="__tabbed_6_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-5-1"><span class="hll"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span><span class="p">,</span> <span class="n">Response</span>
</span></span><span id="__span-5-2">
</span><span id="__span-5-3"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-5-4">
</span><span id="__span-5-5">
</span><span id="__span-5-6"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/legacy/&quot;</span><span class="p">)</span>
</span><span id="__span-5-7"><span class="k">def</span><span class="w"> </span><span class="nf">get_legacy_data</span><span class="p">():</span>
</span><span id="__span-5-8">    <span class="n">data</span> <span class="o">=</span> <span class="s2">&quot;&quot;&quot;&lt;?xml version=&quot;1.0&quot;?&gt;</span>
</span><span id="__span-5-9"><span class="s2">    &lt;shampoo&gt;</span>
</span><span id="__span-5-10"><span class="s2">    &lt;Header&gt;</span>
</span><span id="__span-5-11"><span class="s2">        Apply shampoo here.</span>
</span><span id="__span-5-12"><span class="s2">    &lt;/Header&gt;</span>
</span><span id="__span-5-13"><span class="s2">    &lt;Body&gt;</span>
</span><span id="__span-5-14"><span class="s2">        You&#39;ll have to use soap here.</span>
</span><span id="__span-5-15"><span class="s2">    &lt;/Body&gt;</span>
</span><span id="__span-5-16"><span class="s2">    &lt;/shampoo&gt;</span>
</span><span id="__span-5-17"><span class="s2">    &quot;&quot;&quot;</span>
</span><span id="__span-5-18"><span class="hll">    <span class="k">return</span> <span class="n">Response</span><span class="p">(</span><span class="n">content</span><span class="o">=</span><span class="n">data</span><span class="p">,</span> <span class="n">media_type</span><span class="o">=</span><span class="s2">&quot;application/xml&quot;</span><span class="p">)</span>
</span></span></code></pre></div>
</div>
</div>
</div>
<h3 id="htmlresponse"><code>HTMLResponse</code><a class="headerlink" href="#htmlresponse" title="Permanent link">&para;</a></h3>
<p>Takes some text or bytes and returns an HTML response, as you read above.</p>
<h3 id="plaintextresponse"><code>PlainTextResponse</code><a class="headerlink" href="#plaintextresponse" title="Permanent link">&para;</a></h3>
<p>Takes some text or bytes and returns a plain text response.</p>
<div class="tabbed-set tabbed-alternate" data-tabs="7:1"><input checked="checked" id="__tabbed_7_1" name="__tabbed_7" type="radio" /><div class="tabbed-labels"><label for="__tabbed_7_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-6-1"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-6-2"><span class="hll"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">PlainTextResponse</span>
</span></span><span id="__span-6-3">
</span><span id="__span-6-4"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-6-5">
</span><span id="__span-6-6">
</span><span id="__span-6-7"><span class="hll"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PlainTextResponse</span><span class="p">)</span>
</span></span><span id="__span-6-8"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">main</span><span class="p">():</span>
</span><span id="__span-6-9"><span class="hll">    <span class="k">return</span> <span class="s2">&quot;Hello World&quot;</span>
</span></span></code></pre></div>
</div>
</div>
</div>
<h3 id="jsonresponse"><code>JSONResponse</code><a class="headerlink" href="#jsonresponse" title="Permanent link">&para;</a></h3>
<p>Takes some data and returns an <code>application/json</code> encoded response.</p>
<p>This is the default response used in <strong>FastAPI</strong>, as you read above.</p>
<div class="admonition note">
<p class="admonition-title">Technical Details</p>
<p>But if you declare a response model or return type, that will be used directly to serialize the data to JSON, and a response with the right media type for JSON will be returned directly, without using the <code>JSONResponse</code> class.</p>
<p>This is the ideal way to get the best performance.</p>
</div>
<h3 id="redirectresponse"><code>RedirectResponse</code><a class="headerlink" href="#redirectresponse" title="Permanent link">&para;</a></h3>
<p>Returns an HTTP redirect. Uses a 307 status code (Temporary Redirect) by default.</p>
<p>You can return a <code>RedirectResponse</code> directly:</p>
<div class="tabbed-set tabbed-alternate" data-tabs="8:1"><input checked="checked" id="__tabbed_8_1" name="__tabbed_8" type="radio" /><div class="tabbed-labels"><label for="__tabbed_8_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-7-1"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-7-2"><span class="hll"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">RedirectResponse</span>
</span></span><span id="__span-7-3">
</span><span id="__span-7-4"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-7-5">
</span><span id="__span-7-6">
</span><span id="__span-7-7"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/typer&quot;</span><span class="p">)</span>
</span><span id="__span-7-8"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">redirect_typer</span><span class="p">():</span>
</span><span id="__span-7-9"><span class="hll">    <span class="k">return</span> <span class="n">RedirectResponse</span><span class="p">(</span><span class="s2">&quot;https://typer.tiangolo.com&quot;</span><span class="p">)</span>
</span></span></code></pre></div>
</div>
</div>
</div>
<hr />
<p>Or you can use it in the <code>response_class</code> parameter:</p>
<div class="tabbed-set tabbed-alternate" data-tabs="9:1"><input checked="checked" id="__tabbed_9_1" name="__tabbed_9" type="radio" /><div class="tabbed-labels"><label for="__tabbed_9_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-8-1"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-8-2"><span class="hll"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">RedirectResponse</span>
</span></span><span id="__span-8-3">
</span><span id="__span-8-4"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-8-5">
</span><span id="__span-8-6">
</span><span id="__span-8-7"><span class="hll"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/fastapi&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">RedirectResponse</span><span class="p">)</span>
</span></span><span id="__span-8-8"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">redirect_fastapi</span><span class="p">():</span>
</span><span id="__span-8-9"><span class="hll">    <span class="k">return</span> <span class="s2">&quot;https://fastapi.tiangolo.com&quot;</span>
</span></span></code></pre></div>
</div>
</div>
</div>
<p>If you do that, then you can return the URL directly from your <em>path operation</em> function.</p>
<p>In this case, the <code>status_code</code> used will be the default one for the <code>RedirectResponse</code>, which is <code>307</code>.</p>
<hr />
<p>You can also use the <code>status_code</code> parameter combined with the <code>response_class</code> parameter:</p>
<div class="tabbed-set tabbed-alternate" data-tabs="10:1"><input checked="checked" id="__tabbed_10_1" name="__tabbed_10" type="radio" /><div class="tabbed-labels"><label for="__tabbed_10_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-9-1"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-9-2"><span class="hll"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">RedirectResponse</span>
</span></span><span id="__span-9-3">
</span><span id="__span-9-4"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-9-5">
</span><span id="__span-9-6">
</span><span id="__span-9-7"><span class="hll"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/pydantic&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">RedirectResponse</span><span class="p">,</span> <span class="n">status_code</span><span class="o">=</span><span class="mi">302</span><span class="p">)</span>
</span></span><span id="__span-9-8"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">redirect_pydantic</span><span class="p">():</span>
</span><span id="__span-9-9"><span class="hll">    <span class="k">return</span> <span class="s2">&quot;https://docs.pydantic.dev/&quot;</span>
</span></span></code></pre></div>
</div>
</div>
</div>
<h3 id="streamingresponse"><code>StreamingResponse</code><a class="headerlink" href="#streamingresponse" title="Permanent link">&para;</a></h3>
<p>Takes an async generator or a normal generator/iterator (a function with <code>yield</code>) and streams the response body.</p>
<div class="tabbed-set tabbed-alternate" data-tabs="11:1"><input checked="checked" id="__tabbed_11_1" name="__tabbed_11" type="radio" /><div class="tabbed-labels"><label for="__tabbed_11_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-10-1"><span class="kn">import</span><span class="w"> </span><span class="nn">anyio</span>
</span><span id="__span-10-2"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-10-3"><span class="hll"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">StreamingResponse</span>
</span></span><span id="__span-10-4">
</span><span id="__span-10-5"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-10-6">
</span><span id="__span-10-7">
</span><span id="__span-10-8"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">fake_video_streamer</span><span class="p">():</span>
</span><span id="__span-10-9">    <span class="k">for</span> <span class="n">i</span> <span class="ow">in</span> <span class="nb">range</span><span class="p">(</span><span class="mi">10</span><span class="p">):</span>
</span><span id="__span-10-10">        <span class="k">yield</span> <span class="sa">b</span><span class="s2">&quot;some fake video bytes&quot;</span>
</span><span id="__span-10-11">        <span class="k">await</span> <span class="n">anyio</span><span class="o">.</span><span class="n">sleep</span><span class="p">(</span><span class="mi">0</span><span class="p">)</span>
</span><span id="__span-10-12">
</span><span id="__span-10-13">
</span><span id="__span-10-14"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/&quot;</span><span class="p">)</span>
</span><span id="__span-10-15"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">main</span><span class="p">():</span>
</span><span id="__span-10-16"><span class="hll">    <span class="k">return</span> <span class="n">StreamingResponse</span><span class="p">(</span><span class="n">fake_video_streamer</span><span class="p">())</span>
</span></span></code></pre></div>
</div>
</div>
</div>
<div class="admonition note">
<p class="admonition-title">Technical Details</p>
<p>An <code>async</code> task can only be cancelled when it reaches an <code>await</code>. If there is no <code>await</code>, the generator (function with <code>yield</code>) can not be cancelled properly and may keep running even after cancellation is requested.</p>
<p>Since this small example does not need any <code>await</code> statements, we add an <code>await anyio.sleep(0)</code> to give the event loop a chance to handle cancellation.</p>
<p>This would be even more important with large or infinite streams.</p>
</div>
<div class="admonition tip">
<p class="admonition-title">Tip</p>
<p>Instead of returning a <code>StreamingResponse</code> directly, you should probably follow the style in <a href=".././stream-data/">Stream Data</a>, it's much more convenient and handles cancellation behind the scenes for you.</p>
<p>If you are streaming JSON Lines, follow the <a href="../../tutorial/stream-json-lines/">Stream JSON Lines</a> tutorial.</p>
</div>
<h3 id="fileresponse"><code>FileResponse</code><a class="headerlink" href="#fileresponse" title="Permanent link">&para;</a></h3>
<p>Asynchronously streams a file as the response.</p>
<p>Takes a different set of arguments to instantiate than the other response types:</p>
<ul>
<li><code>path</code> - The file path to the file to stream.</li>
<li><code>headers</code> - Any custom headers to include, as a dictionary.</li>
<li><code>media_type</code> - A string giving the media type. If unset, the filename or path will be used to infer a media type.</li>
<li><code>filename</code> - If set, this will be included in the response <code>Content-Disposition</code>.</li>
</ul>
<p>File responses will include appropriate <code>Content-Length</code>, <code>Last-Modified</code> and <code>ETag</code> headers.</p>
<div class="tabbed-set tabbed-alternate" data-tabs="12:1"><input checked="checked" id="__tabbed_12_1" name="__tabbed_12" type="radio" /><div class="tabbed-labels"><label for="__tabbed_12_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-11-1"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-11-2"><span class="hll"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">FileResponse</span>
</span></span><span id="__span-11-3">
</span><span id="__span-11-4"><span class="n">some_file_path</span> <span class="o">=</span> <span class="s2">&quot;large-video-file.mp4&quot;</span>
</span><span id="__span-11-5"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-11-6">
</span><span id="__span-11-7">
</span><span id="__span-11-8"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/&quot;</span><span class="p">)</span>
</span><span id="__span-11-9"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">main</span><span class="p">():</span>
</span><span id="__span-11-10"><span class="hll">    <span class="k">return</span> <span class="n">FileResponse</span><span class="p">(</span><span class="n">some_file_path</span><span class="p">)</span>
</span></span></code></pre></div>
</div>
</div>
</div>
<p>You can also use the <code>response_class</code> parameter:</p>
<div class="tabbed-set tabbed-alternate" data-tabs="13:1"><input checked="checked" id="__tabbed_13_1" name="__tabbed_13" type="radio" /><div class="tabbed-labels"><label for="__tabbed_13_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-12-1"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-12-2"><span class="hll"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">FileResponse</span>
</span></span><span id="__span-12-3">
</span><span id="__span-12-4"><span class="n">some_file_path</span> <span class="o">=</span> <span class="s2">&quot;large-video-file.mp4&quot;</span>
</span><span id="__span-12-5"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-12-6">
</span><span id="__span-12-7">
</span><span id="__span-12-8"><span class="hll"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">FileResponse</span><span class="p">)</span>
</span></span><span id="__span-12-9"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">main</span><span class="p">():</span>
</span><span id="__span-12-10"><span class="hll">    <span class="k">return</span> <span class="n">some_file_path</span>
</span></span></code></pre></div>
</div>
</div>
</div>
<p>In this case, you can return the file path directly from your <em>path operation</em> function.</p>
<h2 id="custom-response-class">Custom response class<a class="headerlink" href="#custom-response-class" title="Permanent link">&para;</a></h2>
<p>You can create your own custom response class, inheriting from <code>Response</code> and using it.</p>
<p>For example, let's say that you want to use <a href="https://github.com/ijl/orjson"><code>orjson</code></a> with some settings.</p>
<p>Let's say you want it to return indented and formatted JSON, so you want to use the orjson option <code>orjson.OPT_INDENT_2</code>.</p>
<p>You could create a <code>CustomORJSONResponse</code>. The main thing you have to do is create a <code>Response.render(content)</code> method that returns the content as <code>bytes</code>:</p>
<div class="tabbed-set tabbed-alternate" data-tabs="14:1"><input checked="checked" id="__tabbed_14_1" name="__tabbed_14" type="radio" /><div class="tabbed-labels"><label for="__tabbed_14_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-13-1"><span class="kn">from</span><span class="w"> </span><span class="nn">typing</span><span class="w"> </span><span class="kn">import</span> <span class="n">Any</span>
</span><span id="__span-13-2">
</span><span id="__span-13-3"><span class="kn">import</span><span class="w"> </span><span class="nn">orjson</span>
</span><span id="__span-13-4"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span><span class="p">,</span> <span class="n">Response</span>
</span><span id="__span-13-5">
</span><span id="__span-13-6"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-13-7">
</span><span id="__span-13-8">
</span><span id="__span-13-9"><span class="hll"><span class="k">class</span><span class="w"> </span><span class="nc">CustomORJSONResponse</span><span class="p">(</span><span class="n">Response</span><span class="p">):</span>
</span></span><span id="__span-13-10"><span class="hll">    <span class="n">media_type</span> <span class="o">=</span> <span class="s2">&quot;application/json&quot;</span>
</span></span><span id="__span-13-11"><span class="hll">
</span></span><span id="__span-13-12"><span class="hll">    <span class="k">def</span><span class="w"> </span><span class="nf">render</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">content</span><span class="p">:</span> <span class="n">Any</span><span class="p">)</span> <span class="o">-&gt;</span> <span class="nb">bytes</span><span class="p">:</span>
</span></span><span id="__span-13-13"><span class="hll">        <span class="k">assert</span> <span class="n">orjson</span> <span class="ow">is</span> <span class="ow">not</span> <span class="kc">None</span><span class="p">,</span> <span class="s2">&quot;orjson must be installed&quot;</span>
</span></span><span id="__span-13-14"><span class="hll">        <span class="k">return</span> <span class="n">orjson</span><span class="o">.</span><span class="n">dumps</span><span class="p">(</span><span class="n">content</span><span class="p">,</span> <span class="n">option</span><span class="o">=</span><span class="n">orjson</span><span class="o">.</span><span class="n">OPT_INDENT_2</span><span class="p">)</span>
</span></span><span id="__span-13-15">
</span><span id="__span-13-16">
</span><span id="__span-13-17"><span class="hll"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">CustomORJSONResponse</span><span class="p">)</span>
</span></span><span id="__span-13-18"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">main</span><span class="p">():</span>
</span><span id="__span-13-19">    <span class="k">return</span> <span class="p">{</span><span class="s2">&quot;message&quot;</span><span class="p">:</span> <span class="s2">&quot;Hello World&quot;</span><span class="p">}</span>
</span></code></pre></div>
</div>
</div>
</div>
<p>Now instead of returning:</p>
<div class="highlight"><pre><span></span><code><span id="__span-14-1"><span class="p">{</span><span class="nt">&quot;message&quot;</span><span class="p">:</span><span class="w"> </span><span class="s2">&quot;Hello World&quot;</span><span class="p">}</span>
</span></code></pre></div>
<p>...this response will return:</p>
<div class="highlight"><pre><span></span><code><span id="__span-15-1"><span class="p">{</span>
</span><span id="__span-15-2"><span class="w">  </span><span class="nt">&quot;message&quot;</span><span class="p">:</span><span class="w"> </span><span class="s2">&quot;Hello World&quot;</span>
</span><span id="__span-15-3"><span class="p">}</span>
</span></code></pre></div>
<p>Of course, you will probably find much better ways to take advantage of this than formatting JSON. 😉</p>
<h3 id="orjson-or-response-model"><code>orjson</code> or Response Model<a class="headerlink" href="#orjson-or-response-model" title="Permanent link">&para;</a></h3>
<p>If what you are looking for is performance, you are probably better off using a <a href="../../tutorial/response-model/">Response Model</a> than an <code>orjson</code> response.</p>
<p>With a response model, FastAPI will use Pydantic to serialize the data to JSON, without using intermediate steps, like converting it with <code>jsonable_encoder</code>, which would happen in any other case.</p>
<p>And under the hood, Pydantic uses the same underlying Rust mechanisms as <code>orjson</code> to serialize to JSON, so you will already get the best performance with a response model.</p>
<h2 id="default-response-class">Default response class<a class="headerlink" href="#default-response-class" title="Permanent link">&para;</a></h2>
<p>When creating a <strong>FastAPI</strong> class instance or an <code>APIRouter</code> you can specify which response class to use by default.</p>
<p>The parameter that defines this is <code>default_response_class</code>.</p>
<p>In the example below, <strong>FastAPI</strong> will use <code>HTMLResponse</code> by default, in all <em>path operations</em>, instead of JSON.</p>
<div class="tabbed-set tabbed-alternate" data-tabs="15:1"><input checked="checked" id="__tabbed_15_1" name="__tabbed_15" type="radio" /><div class="tabbed-labels"><label for="__tabbed_15_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-16-1"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-16-2"><span class="hll"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">HTMLResponse</span>
</span></span><span id="__span-16-3">
</span><span id="__span-16-4"><span class="hll"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">(</span><span class="n">default_response_class</span><span class="o">=</span><span class="n">HTMLResponse</span><span class="p">)</span>
</span></span><span id="__span-16-5">
</span><span id="__span-16-6">
</span><span id="__span-16-7"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/items/&quot;</span><span class="p">)</span>
</span><span id="__span-16-8"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">read_items</span><span class="p">():</span>
</span><span id="__span-16-9">    <span class="k">return</span> <span class="s2">&quot;&lt;h1&gt;Items&lt;/h1&gt;&lt;p&gt;This is a list of items.&lt;/p&gt;&quot;</span>
</span></code></pre></div>
</div>
</div>
</div>
<div class="admonition tip">
<p class="admonition-title">Tip</p>
<p>You can still override <code>response_class</code> in <em>path operations</em> as before.</p>
</div>
<h2 id="additional-documentation">Additional documentation<a class="headerlink" href="#additional-documentation" title="Permanent link">&para;</a></h2>
<p>You can also declare the media type and many other details in OpenAPI using <code>responses</code>: <a href="../additional-responses/">Additional Responses in OpenAPI</a>.</p>















              </article>
            </div>
          
          
  <script>var tabs=__md_get("__tabs");if(Array.isArray(tabs))e:for(var set of document.querySelectorAll(".tabbed-set")){var labels=set.querySelector(".tabbed-labels");for(var tab of tabs)for(var label of labels.getElementsByTagName("label"))if(label.innerText.trim()===tab){var input=document.getElementById(label.htmlFor);input.checked=!0;continue e}}</script>

<script>var target=document.getElementById(location.hash.slice(1));target&&target.name&&(target.checked=target.name.startsWith("__tabbed_"))</script>
        </div>
        
          <button type="button" class="md-top md-icon" data-md-component="top" hidden>
  
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M13 20h-2V8l-5.5 5.5-1.42-1.42L12 4.16l7.92 7.92-1.42 1.42L13 8z"/></svg>
  Back to top
</button>
        
      </main>
      
        <footer class="md-footer">
  
    
      
      <nav class="md-footer__inner md-grid" aria-label="Footer" >
        
          
          <a href="../response-directly/" class="md-footer__link md-footer__link--prev" aria-label="Previous: Return a Response Directly">
            <div class="md-footer__button md-icon">
              
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M20 11v2H8l5.5 5.5-1.42 1.42L4.16 12l7.92-7.92L13.5 5.5 8 11z"/></svg>
            </div>
            <div class="md-footer__title">
              <span class="md-footer__direction">
                Previous
              </span>
              <div class="md-ellipsis">
                Return a Response Directly
              </div>
            </div>
          </a>
        
        
          
          <a href="../additional-responses/" class="md-footer__link md-footer__link--next" aria-label="Next: Additional Responses in OpenAPI">
            <div class="md-footer__title">
              <span class="md-footer__direction">
                Next
              </span>
              <div class="md-ellipsis">
                Additional Responses in OpenAPI
              </div>
            </div>
            <div class="md-footer__button md-icon">
              
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M4 11v2h12l-5.5 5.5 1.42 1.42L19.84 12l-7.92-7.92L10.5 5.5 16 11z"/></svg>
            </div>
          </a>
        
      </nav>
    
  
  <div class="md-footer-meta md-typeset">
    <div class="md-footer-meta__inner md-grid">
      <div class="md-copyright">
    <div class="md-copyright__highlight">
        The FastAPI trademark is owned by <a href="https://tiangolo.com" target="_blank">@tiangolo</a> and is registered in the US and across other regions
    </div>
    
    Made with
    <a href="https://zensical.org" target="_blank" rel="noopener">
        Zensical
    </a>
    
</div>
      
        
<div class="md-social">
  
    
    
    
    
      
      
    
    <a href="https://github.com/fastapi/fastapi" target="_blank" rel="noopener" title="github.com" class="md-social__link">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M10.226 17.284c-2.965-.36-5.054-2.493-5.054-5.256 0-1.123.404-2.336 1.078-3.144-.292-.741-.247-2.314.09-2.965.898-.112 2.111.36 2.83 1.01.853-.269 1.752-.404 2.853-.404 1.1 0 1.999.135 2.807.382.696-.629 1.932-1.1 2.83-.988.315.606.36 2.179.067 2.942.72.854 1.101 2 1.101 3.167 0 2.763-2.089 4.852-5.098 5.234.763.494 1.28 1.572 1.28 2.807v2.336c0 .674.561 1.056 1.235.786 4.066-1.55 7.255-5.615 7.255-10.646C23.5 6.188 18.334 1 11.978 1 5.62 1 .5 6.188.5 12.545c0 4.986 3.167 9.12 7.435 10.669.606.225 1.19-.18 1.19-.786V20.63a2.9 2.9 0 0 1-1.078.224c-1.483 0-2.359-.808-2.987-2.313-.247-.607-.517-.966-1.034-1.033-.27-.023-.359-.135-.359-.27 0-.27.45-.471.898-.471.652 0 1.213.404 1.797 1.235.45.651.921.943 1.483.943.561 0 .92-.202 1.437-.719.382-.381.674-.718.944-.943"/></svg>
    </a>
  
    
    
    
    
      
      
    
    <a href="https://discord.com/invite/VQjSZaeJmf" target="_blank" rel="noopener" title="discord.com" class="md-social__link">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--! Font Awesome Free 7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free (Icons: CC BY 4.0, Fonts: SIL OFL 1.1, Code: MIT License) Copyright 2026 Fonticons, Inc.--><path fill="currentColor" d="M492.5 69.8c-.2-.3-.4-.6-.8-.7-38.1-17.5-78.4-30-119.7-37.1-.4-.1-.8 0-1.1.1s-.6.4-.8.8c-5.5 9.9-10.5 20.2-14.9 30.6-44.6-6.8-89.9-6.8-134.4 0-4.5-10.5-9.5-20.7-15.1-30.6-.2-.3-.5-.6-.8-.8s-.7-.2-1.1-.2C162.5 39 122.2 51.5 84.1 69c-.3.1-.6.4-.8.7C7.1 183.5-13.8 294.6-3.6 404.2c0 .3.1.5.2.8s.3.4.5.6c44.4 32.9 94 58 146.8 74.2.4.1.8.1 1.1 0s.7-.4.9-.7c11.3-15.4 21.4-31.8 30-48.8.1-.2.2-.5.2-.8s0-.5-.1-.8-.2-.5-.4-.6-.4-.3-.7-.4c-15.8-6.1-31.2-13.4-45.9-21.9-.3-.2-.5-.4-.7-.6s-.3-.6-.3-.9 0-.6.2-.9.3-.5.6-.7c3.1-2.3 6.2-4.7 9.1-7.1.3-.2.6-.4.9-.4s.7 0 1 .1c96.2 43.9 200.4 43.9 295.5 0 .3-.1.7-.2 1-.2s.7.2.9.4c2.9 2.4 6 4.9 9.1 7.2.2.2.4.4.6.7s.2.6.2.9-.1.6-.3.9-.4.5-.6.6c-14.7 8.6-30 15.9-45.9 21.8-.2.1-.5.2-.7.4s-.3.4-.4.7-.1.5-.1.8.1.5.2.8c8.8 17 18.8 33.3 30 48.8.2.3.6.6.9.7s.8.1 1.1 0c52.9-16.2 102.6-41.3 147.1-74.2.2-.2.4-.4.5-.6s.2-.5.2-.8c12.3-126.8-20.5-236.9-86.9-334.5zm-302 267.7c-29 0-52.8-26.6-52.8-59.2s23.4-59.2 52.8-59.2c29.7 0 53.3 26.8 52.8 59.2 0 32.7-23.4 59.2-52.8 59.2m195.4 0c-29 0-52.8-26.6-52.8-59.2s23.4-59.2 52.8-59.2c29.7 0 53.3 26.8 52.8 59.2 0 32.7-23.2 59.2-52.8 59.2"/></svg>
    </a>
  
    
    
    
    
      
      
    
    <a href="https://x.com/fastapi" target="_blank" rel="noopener" title="x.com" class="md-social__link">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free (Icons: CC BY 4.0, Fonts: SIL OFL 1.1, Code: MIT License) Copyright 2026 Fonticons, Inc.--><path fill="currentColor" d="M357.2 48h70.6L273.6 224.2 455 464H313L201.7 318.6 74.5 464H3.8l164.9-188.5L-5.2 48h145.6l100.5 132.9zm-24.8 373.8h39.1L119.1 88h-42z"/></svg>
    </a>
  
    
    
    
    
      
      
    
    <a href="https://bsky.app/profile/fastapi.tiangolo.com" target="_blank" rel="noopener" title="bsky.app" class="md-social__link">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--! Font Awesome Free 7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free (Icons: CC BY 4.0, Fonts: SIL OFL 1.1, Code: MIT License) Copyright 2026 Fonticons, Inc.--><path fill="currentColor" d="M407.8 294.7c-3.3-.4-6.7-.8-10-1.3 3.4.4 6.7.9 10 1.3M288 227.1c-26.1-50.7-97.1-145.2-163.1-191.8C61.6-9.4 37.5-1.7 21.6 5.5 3.3 13.8 0 41.9 0 58.4S9.1 194 15 213.9c19.5 65.7 89.1 87.9 153.2 80.7 3.3-.5 6.6-.9 10-1.4-3.3.5-6.6 1-10 1.4-93.9 14-177.3 48.2-67.9 169.9C220.6 589.1 265.1 437.8 288 361.1c22.9 76.7 49.2 222.5 185.6 103.4 102.4-103.4 28.1-156-65.8-169.9-3.3-.4-6.7-.8-10-1.3 3.4.4 6.7.9 10 1.3 64.1 7.1 133.6-15.1 153.2-80.7C566.9 194 576 75 576 58.4s-3.3-44.7-21.6-52.9c-15.8-7.1-40-14.9-103.2 29.8C385.1 81.9 314.1 176.4 288 227.1"/></svg>
    </a>
  
    
    
    
    
      
      
    
    <a href="https://www.linkedin.com/company/fastapi" target="_blank" rel="noopener" title="www.linkedin.com" class="md-social__link">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free (Icons: CC BY 4.0, Fonts: SIL OFL 1.1, Code: MIT License) Copyright 2026 Fonticons, Inc.--><path fill="currentColor" d="M416 32H31.9C14.3 32 0 46.5 0 64.3v383.4C0 465.5 14.3 480 31.9 480H416c17.6 0 32-14.5 32-32.3V64.3c0-17.8-14.4-32.3-32-32.3M135.4 416H69V202.2h66.5V416zM102.2 96a38.5 38.5 0 1 1 0 77 38.5 38.5 0 1 1 0-77m282.1 320h-66.4V312c0-24.8-.5-56.7-34.5-56.7-34.6 0-39.9 27-39.9 54.9V416h-66.4V202.2h63.7v29.2h.9c8.9-16.8 30.6-34.5 62.9-34.5 67.2 0 79.7 44.3 79.7 101.9z"/></svg>
    </a>
  
</div>
      
    </div>
  </div>
</footer>
      
    </div>
    <div class="md-dialog" data-md-component="dialog">
      <div class="md-dialog__inner md-typeset"></div>
    </div>
    
      <div class="md-progress" data-md-component="progress" role="progressbar"></div>
    
    
    
      
      
      <script id="__config" type="application/json">{"annotate":null,"base":"../..","features":["content.code.annotate","content.code.copy","content.footnote.tooltips","content.tabs.link","content.tooltips","navigation.footer","navigation.indexes","navigation.instant","navigation.instant.prefetch","navigation.instant.progress","navigation.path","navigation.tabs","navigation.tabs.sticky","navigation.top","navigation.tracking","search.highlight","search.share","search.suggest","toc.follow"],"search":"../../assets/javascripts/workers/search.b6b7e04f.min.js","tags":null,"translations":{"clipboard.copied":"Copied to clipboard","clipboard.copy":"Copy to clipboard","search.result.more.one":"1 more on this page","search.result.more.other":"# more on this page","search.result.none":"No matching documents","search.result.one":"1 matching document","search.result.other":"# matching documents","search.result.placeholder":"Type to start searching","search.result.term.missing":"Missing","select.version":"Select version"},"version":null}</script>
    
    
      <script src="../../assets/javascripts/bundle.d7f30b55.min.js"></script>
      
        <script src="../../js/termynal.js"></script>
      
        <script src="../../js/custom.js"></script>
      
        <script src="../../js/init_kapa_widget.js"></script>
      
    
  <!-- Cloudflare Pages Analytics --><script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "83c63961621f43319d43d493c35d7611"}'></script><!-- Cloudflare Pages Analytics --></body>
</html>