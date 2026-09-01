
<!doctype html>
<html lang="en" class="no-js">
  <head>
    
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width,initial-scale=1">
      
        <meta name="description" content="FastAPI framework, high performance, easy to learn, fast to code, ready for production">
      
      
      
        <link rel="canonical" href="https://fastapi.tiangolo.com/advanced/stream-data/">
      
      
        <link rel="prev" href="../">
      
      
        <link rel="next" href="../path-operation-advanced-configuration/">
      
      
        
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
    
    
      
        <title>Stream Data - FastAPI</title>
      
    
    
      
        
      
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
      
        
        <a href="#stream-data" class="md-skip">
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
            
              Stream Data
            
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
            
              
            
              
                
  
  
    
  
  
  
    <li class="md-nav__item md-nav__item--active">
      
      
        <input class="md-nav__toggle md-toggle" type="checkbox" id="__toc">
      
      
      
        
      
      
        <label class="md-nav__link md-nav__link--active" for="__toc">
          
  
  
  <span class="md-ellipsis">
    
  
  Stream Data

    
  </span>
  
  

          <span class="md-nav__icon md-icon"></span>
        </label>
      
      <a href="././" class="md-nav__link md-nav__link--active">
        
  
  
  <span class="md-ellipsis">
    
  
  Stream Data

    
  </span>
  
  

      </a>
      
        


<nav class="md-nav md-nav--secondary" aria-label="On this page">
  
  
  
    
  
  
    <label class="md-nav__title" for="__toc">
      <span class="md-nav__icon md-icon"></span>
      On this page
    </label>
    <ul class="md-nav__list" data-md-component="toc" data-md-scrollfix>
      
        <li class="md-nav__item">
  <a href="#use-cases" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Use Cases
      </span>
    </span>
  </a>
  
</li>
      
        <li class="md-nav__item">
  <a href="#a-streamingresponse-with-yield" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        A <code>StreamingResponse</code> with <code>yield</code>
      </span>
    </span>
  </a>
  
    <nav class="md-nav" aria-label="A StreamingResponse with yield">
      <ul class="md-nav__list">
        
          <li class="md-nav__item">
  <a href="#non-async-path-operation-functions" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Non-async <em>path operation functions</em>
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#no-annotation" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        No Annotation
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#stream-bytes" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Stream Bytes
      </span>
    </span>
  </a>
  
</li>
        
      </ul>
    </nav>
  
</li>
      
        <li class="md-nav__item">
  <a href="#a-custom-pngstreamingresponse" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        A Custom <code>PNGStreamingResponse</code>
      </span>
    </span>
  </a>
  
    <nav class="md-nav" aria-label="A Custom PNGStreamingResponse">
      <ul class="md-nav__list">
        
          <li class="md-nav__item">
  <a href="#simulate-a-file" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Simulate a File
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#files-and-async" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Files and Async
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#yield-from" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        <code>yield from</code>
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
  

              
            
              
                
  
  
  
  
    <li class="md-nav__item">
      <a href="../custom-response/" class="md-nav__link">
        
  
  
  <span class="md-ellipsis">
    
  
  Custom Response - HTML, Stream, File, others

    
  </span>
  
  

      </a>
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
  <a href="#use-cases" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Use Cases
      </span>
    </span>
  </a>
  
</li>
      
        <li class="md-nav__item">
  <a href="#a-streamingresponse-with-yield" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        A <code>StreamingResponse</code> with <code>yield</code>
      </span>
    </span>
  </a>
  
    <nav class="md-nav" aria-label="A StreamingResponse with yield">
      <ul class="md-nav__list">
        
          <li class="md-nav__item">
  <a href="#non-async-path-operation-functions" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Non-async <em>path operation functions</em>
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#no-annotation" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        No Annotation
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#stream-bytes" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Stream Bytes
      </span>
    </span>
  </a>
  
</li>
        
      </ul>
    </nav>
  
</li>
      
        <li class="md-nav__item">
  <a href="#a-custom-pngstreamingresponse" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        A Custom <code>PNGStreamingResponse</code>
      </span>
    </span>
  </a>
  
    <nav class="md-nav" aria-label="A Custom PNGStreamingResponse">
      <ul class="md-nav__list">
        
          <li class="md-nav__item">
  <a href="#simulate-a-file" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Simulate a File
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#files-and-async" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        Files and Async
      </span>
    </span>
  </a>
  
</li>
        
          <li class="md-nav__item">
  <a href="#yield-from" class="md-nav__link">
    <span class="md-ellipsis">
      <span class="md-typeset">
        <code>yield from</code>
      </span>
    </span>
  </a>
  
</li>
        
      </ul>
    </nav>
  
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
                
  
  
  
  


<h1 id="stream-data">Stream Data<a class="headerlink" href="#stream-data" title="Permanent link">&para;</a></h1>
<p>If you want to stream data that can be structured as JSON, you should <a href="../../tutorial/stream-json-lines/">Stream JSON Lines</a>.</p>
<p>But if you want to <strong>stream pure binary data</strong> or strings, here's how you can do it.</p>
<div class="admonition note">
<p class="admonition-title">Note</p>
<p>Added in FastAPI 0.134.0.</p>
</div>
<h2 id="use-cases">Use Cases<a class="headerlink" href="#use-cases" title="Permanent link">&para;</a></h2>
<p>You could use this if you want to stream pure strings, for example directly from the output of an <strong>AI LLM</strong> service.</p>
<p>You could also use it to stream <strong>large binary files</strong>, where you stream each chunk of data as you read it, without having to read it all into memory at once.</p>
<p>You could also stream <strong>video</strong> or <strong>audio</strong> this way, it could even be generated as you process and send it.</p>
<h2 id="a-streamingresponse-with-yield">A <code>StreamingResponse</code> with <code>yield</code><a class="headerlink" href="#a-streamingresponse-with-yield" title="Permanent link">&para;</a></h2>
<p>If you declare a <code>response_class=StreamingResponse</code> in your <em>path operation function</em>, you can use <code>yield</code> to send each chunk of data in turn.</p>
<div class="tabbed-set tabbed-alternate" data-tabs="1:1"><input checked="checked" id="__tabbed_1_1" name="__tabbed_1" type="radio" /><div class="tabbed-labels"><label for="__tabbed_1_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-0-1"><span class="kn">from</span><span class="w"> </span><span class="nn">collections.abc</span><span class="w"> </span><span class="kn">import</span> <span class="n">AsyncIterable</span><span class="p">,</span> <span class="n">Iterable</span>
</span><span id="__span-0-2">
</span><span id="__span-0-3"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-0-4"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">StreamingResponse</span>
</span><span id="__span-0-5">
</span><span id="__span-0-6"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-0-7">
</span><span id="__span-0-8">
</span><span id="__span-0-9"><span class="n">message</span> <span class="o">=</span> <span class="s2">&quot;&quot;&quot;</span>
</span><span id="__span-0-10"><span class="s2">Rick: (stumbles in drunkenly, and turns on the lights) Morty! You gotta come on. You got--... you gotta come with me.</span>
</span><span id="__span-0-11"><span class="s2">Morty: (rubs his eyes) What, Rick? What&#39;s going on?</span>
</span><span id="__span-0-12"><span class="s2">Rick: I got a surprise for you, Morty.</span>
</span><span id="__span-0-13"><span class="s2">Morty: It&#39;s the middle of the night. What are you talking about?</span>
</span><span id="__span-0-14"><span class="s2">Rick: (spills alcohol on Morty&#39;s bed) Come on, I got a surprise for you. (drags Morty by the ankle) Come on, hurry up. (pulls Morty out of his bed and into the hall)</span>
</span><span id="__span-0-15"><span class="s2">Morty: Ow! Ow! You&#39;re tugging me too hard!</span>
</span><span id="__span-0-16"><span class="s2">Rick: We gotta go, gotta get outta here, come on. Got a surprise for you Morty.</span>
</span><span id="__span-0-17"><span class="s2">&quot;&quot;&quot;</span>
</span><span id="__span-0-18">
</span><span id="__span-0-19">
</span><span id="__span-0-20"><span class="hll"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span></span><span id="__span-0-21"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_story</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">AsyncIterable</span><span class="p">[</span><span class="nb">str</span><span class="p">]:</span>
</span><span id="__span-0-22">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-0-23"><span class="hll">        <span class="k">yield</span> <span class="n">line</span>
</span></span><span id="__span-0-24">
</span><span id="__span-0-25"><span class="c1"># Code below omitted 👇</span>
</span></code></pre></div>
</div>
</div>
</div>
<details>
<summary>👀 Full file preview</summary>
<div class="tabbed-set tabbed-alternate" data-tabs="2:1"><input checked="checked" id="__tabbed_2_1" name="__tabbed_2" type="radio" /><div class="tabbed-labels"><label for="__tabbed_2_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-1-1"><span class="kn">from</span><span class="w"> </span><span class="nn">collections.abc</span><span class="w"> </span><span class="kn">import</span> <span class="n">AsyncIterable</span><span class="p">,</span> <span class="n">Iterable</span>
</span><span id="__span-1-2">
</span><span id="__span-1-3"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-1-4"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">StreamingResponse</span>
</span><span id="__span-1-5">
</span><span id="__span-1-6"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-1-7">
</span><span id="__span-1-8">
</span><span id="__span-1-9"><span class="n">message</span> <span class="o">=</span> <span class="s2">&quot;&quot;&quot;</span>
</span><span id="__span-1-10"><span class="s2">Rick: (stumbles in drunkenly, and turns on the lights) Morty! You gotta come on. You got--... you gotta come with me.</span>
</span><span id="__span-1-11"><span class="s2">Morty: (rubs his eyes) What, Rick? What&#39;s going on?</span>
</span><span id="__span-1-12"><span class="s2">Rick: I got a surprise for you, Morty.</span>
</span><span id="__span-1-13"><span class="s2">Morty: It&#39;s the middle of the night. What are you talking about?</span>
</span><span id="__span-1-14"><span class="s2">Rick: (spills alcohol on Morty&#39;s bed) Come on, I got a surprise for you. (drags Morty by the ankle) Come on, hurry up. (pulls Morty out of his bed and into the hall)</span>
</span><span id="__span-1-15"><span class="s2">Morty: Ow! Ow! You&#39;re tugging me too hard!</span>
</span><span id="__span-1-16"><span class="s2">Rick: We gotta go, gotta get outta here, come on. Got a surprise for you Morty.</span>
</span><span id="__span-1-17"><span class="s2">&quot;&quot;&quot;</span>
</span><span id="__span-1-18">
</span><span id="__span-1-19">
</span><span id="__span-1-20"><span class="hll"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span></span><span id="__span-1-21"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_story</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">AsyncIterable</span><span class="p">[</span><span class="nb">str</span><span class="p">]:</span>
</span><span id="__span-1-22">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-1-23"><span class="hll">        <span class="k">yield</span> <span class="n">line</span>
</span></span><span id="__span-1-24">
</span><span id="__span-1-25">
</span><span id="__span-1-26"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-async&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-1-27"><span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_async</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">str</span><span class="p">]:</span>
</span><span id="__span-1-28">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-1-29">        <span class="k">yield</span> <span class="n">line</span>
</span><span id="__span-1-30">
</span><span id="__span-1-31">
</span><span id="__span-1-32"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-annotation&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-1-33"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_annotation</span><span class="p">():</span>
</span><span id="__span-1-34">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-1-35">        <span class="k">yield</span> <span class="n">line</span>
</span><span id="__span-1-36">
</span><span id="__span-1-37">
</span><span id="__span-1-38"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-async-no-annotation&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-1-39"><span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_async_no_annotation</span><span class="p">():</span>
</span><span id="__span-1-40">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-1-41">        <span class="k">yield</span> <span class="n">line</span>
</span><span id="__span-1-42">
</span><span id="__span-1-43">
</span><span id="__span-1-44"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-bytes&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-1-45"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_story_bytes</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">AsyncIterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-1-46">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-1-47">        <span class="k">yield</span> <span class="n">line</span><span class="o">.</span><span class="n">encode</span><span class="p">(</span><span class="s2">&quot;utf-8&quot;</span><span class="p">)</span>
</span><span id="__span-1-48">
</span><span id="__span-1-49">
</span><span id="__span-1-50"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-async-bytes&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-1-51"><span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_async_bytes</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-1-52">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-1-53">        <span class="k">yield</span> <span class="n">line</span><span class="o">.</span><span class="n">encode</span><span class="p">(</span><span class="s2">&quot;utf-8&quot;</span><span class="p">)</span>
</span><span id="__span-1-54">
</span><span id="__span-1-55">
</span><span id="__span-1-56"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-annotation-bytes&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-1-57"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_annotation_bytes</span><span class="p">():</span>
</span><span id="__span-1-58">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-1-59">        <span class="k">yield</span> <span class="n">line</span><span class="o">.</span><span class="n">encode</span><span class="p">(</span><span class="s2">&quot;utf-8&quot;</span><span class="p">)</span>
</span><span id="__span-1-60">
</span><span id="__span-1-61">
</span><span id="__span-1-62"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-async-no-annotation-bytes&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-1-63"><span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_async_no_annotation_bytes</span><span class="p">():</span>
</span><span id="__span-1-64">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-1-65">        <span class="k">yield</span> <span class="n">line</span><span class="o">.</span><span class="n">encode</span><span class="p">(</span><span class="s2">&quot;utf-8&quot;</span><span class="p">)</span>
</span></code></pre></div>
</div>
</div>
</div>
</details>
<p>FastAPI will give each chunk of data to the <code>StreamingResponse</code> as is, it won't try to convert it to JSON or anything similar.</p>
<h3 id="non-async-path-operation-functions">Non-async <em>path operation functions</em><a class="headerlink" href="#non-async-path-operation-functions" title="Permanent link">&para;</a></h3>
<p>You can also use regular <code>def</code> functions (without <code>async</code>), and use <code>yield</code> the same way.</p>
<div class="tabbed-set tabbed-alternate" data-tabs="3:1"><input checked="checked" id="__tabbed_3_1" name="__tabbed_3" type="radio" /><div class="tabbed-labels"><label for="__tabbed_3_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-2-1"><span class="c1"># Code above omitted 👆</span>
</span><span id="__span-2-2">
</span><span id="__span-2-3"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-async&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-2-4"><span class="hll"><span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_async</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">str</span><span class="p">]:</span>
</span></span><span id="__span-2-5">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-2-6">        <span class="k">yield</span> <span class="n">line</span>
</span><span id="__span-2-7">
</span><span id="__span-2-8"><span class="c1"># Code below omitted 👇</span>
</span></code></pre></div>
</div>
</div>
</div>
<details>
<summary>👀 Full file preview</summary>
<div class="tabbed-set tabbed-alternate" data-tabs="4:1"><input checked="checked" id="__tabbed_4_1" name="__tabbed_4" type="radio" /><div class="tabbed-labels"><label for="__tabbed_4_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-3-1"><span class="kn">from</span><span class="w"> </span><span class="nn">collections.abc</span><span class="w"> </span><span class="kn">import</span> <span class="n">AsyncIterable</span><span class="p">,</span> <span class="n">Iterable</span>
</span><span id="__span-3-2">
</span><span id="__span-3-3"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-3-4"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">StreamingResponse</span>
</span><span id="__span-3-5">
</span><span id="__span-3-6"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-3-7">
</span><span id="__span-3-8">
</span><span id="__span-3-9"><span class="n">message</span> <span class="o">=</span> <span class="s2">&quot;&quot;&quot;</span>
</span><span id="__span-3-10"><span class="s2">Rick: (stumbles in drunkenly, and turns on the lights) Morty! You gotta come on. You got--... you gotta come with me.</span>
</span><span id="__span-3-11"><span class="s2">Morty: (rubs his eyes) What, Rick? What&#39;s going on?</span>
</span><span id="__span-3-12"><span class="s2">Rick: I got a surprise for you, Morty.</span>
</span><span id="__span-3-13"><span class="s2">Morty: It&#39;s the middle of the night. What are you talking about?</span>
</span><span id="__span-3-14"><span class="s2">Rick: (spills alcohol on Morty&#39;s bed) Come on, I got a surprise for you. (drags Morty by the ankle) Come on, hurry up. (pulls Morty out of his bed and into the hall)</span>
</span><span id="__span-3-15"><span class="s2">Morty: Ow! Ow! You&#39;re tugging me too hard!</span>
</span><span id="__span-3-16"><span class="s2">Rick: We gotta go, gotta get outta here, come on. Got a surprise for you Morty.</span>
</span><span id="__span-3-17"><span class="s2">&quot;&quot;&quot;</span>
</span><span id="__span-3-18">
</span><span id="__span-3-19">
</span><span id="__span-3-20"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-3-21"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_story</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">AsyncIterable</span><span class="p">[</span><span class="nb">str</span><span class="p">]:</span>
</span><span id="__span-3-22">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-3-23">        <span class="k">yield</span> <span class="n">line</span>
</span><span id="__span-3-24">
</span><span id="__span-3-25">
</span><span id="__span-3-26"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-async&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-3-27"><span class="hll"><span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_async</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">str</span><span class="p">]:</span>
</span></span><span id="__span-3-28">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-3-29">        <span class="k">yield</span> <span class="n">line</span>
</span><span id="__span-3-30">
</span><span id="__span-3-31">
</span><span id="__span-3-32"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-annotation&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-3-33"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_annotation</span><span class="p">():</span>
</span><span id="__span-3-34">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-3-35">        <span class="k">yield</span> <span class="n">line</span>
</span><span id="__span-3-36">
</span><span id="__span-3-37">
</span><span id="__span-3-38"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-async-no-annotation&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-3-39"><span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_async_no_annotation</span><span class="p">():</span>
</span><span id="__span-3-40">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-3-41">        <span class="k">yield</span> <span class="n">line</span>
</span><span id="__span-3-42">
</span><span id="__span-3-43">
</span><span id="__span-3-44"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-bytes&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-3-45"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_story_bytes</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">AsyncIterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-3-46">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-3-47">        <span class="k">yield</span> <span class="n">line</span><span class="o">.</span><span class="n">encode</span><span class="p">(</span><span class="s2">&quot;utf-8&quot;</span><span class="p">)</span>
</span><span id="__span-3-48">
</span><span id="__span-3-49">
</span><span id="__span-3-50"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-async-bytes&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-3-51"><span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_async_bytes</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-3-52">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-3-53">        <span class="k">yield</span> <span class="n">line</span><span class="o">.</span><span class="n">encode</span><span class="p">(</span><span class="s2">&quot;utf-8&quot;</span><span class="p">)</span>
</span><span id="__span-3-54">
</span><span id="__span-3-55">
</span><span id="__span-3-56"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-annotation-bytes&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-3-57"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_annotation_bytes</span><span class="p">():</span>
</span><span id="__span-3-58">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-3-59">        <span class="k">yield</span> <span class="n">line</span><span class="o">.</span><span class="n">encode</span><span class="p">(</span><span class="s2">&quot;utf-8&quot;</span><span class="p">)</span>
</span><span id="__span-3-60">
</span><span id="__span-3-61">
</span><span id="__span-3-62"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-async-no-annotation-bytes&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-3-63"><span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_async_no_annotation_bytes</span><span class="p">():</span>
</span><span id="__span-3-64">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-3-65">        <span class="k">yield</span> <span class="n">line</span><span class="o">.</span><span class="n">encode</span><span class="p">(</span><span class="s2">&quot;utf-8&quot;</span><span class="p">)</span>
</span></code></pre></div>
</div>
</div>
</div>
</details>
<h3 id="no-annotation">No Annotation<a class="headerlink" href="#no-annotation" title="Permanent link">&para;</a></h3>
<p>You don't really need to declare the return type annotation for streaming binary data.</p>
<p>As FastAPI will not try to convert the data to JSON with Pydantic or serialize it in any way, in this case, the type annotation is only for your editor and tools to use, it won't be used by FastAPI.</p>
<div class="tabbed-set tabbed-alternate" data-tabs="5:1"><input checked="checked" id="__tabbed_5_1" name="__tabbed_5" type="radio" /><div class="tabbed-labels"><label for="__tabbed_5_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-4-1"><span class="c1"># Code above omitted 👆</span>
</span><span id="__span-4-2">
</span><span id="__span-4-3"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-annotation&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-4-4"><span class="hll"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_annotation</span><span class="p">():</span>
</span></span><span id="__span-4-5">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-4-6">        <span class="k">yield</span> <span class="n">line</span>
</span><span id="__span-4-7">
</span><span id="__span-4-8"><span class="c1"># Code below omitted 👇</span>
</span></code></pre></div>
</div>
</div>
</div>
<details>
<summary>👀 Full file preview</summary>
<div class="tabbed-set tabbed-alternate" data-tabs="6:1"><input checked="checked" id="__tabbed_6_1" name="__tabbed_6" type="radio" /><div class="tabbed-labels"><label for="__tabbed_6_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-5-1"><span class="kn">from</span><span class="w"> </span><span class="nn">collections.abc</span><span class="w"> </span><span class="kn">import</span> <span class="n">AsyncIterable</span><span class="p">,</span> <span class="n">Iterable</span>
</span><span id="__span-5-2">
</span><span id="__span-5-3"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-5-4"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">StreamingResponse</span>
</span><span id="__span-5-5">
</span><span id="__span-5-6"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-5-7">
</span><span id="__span-5-8">
</span><span id="__span-5-9"><span class="n">message</span> <span class="o">=</span> <span class="s2">&quot;&quot;&quot;</span>
</span><span id="__span-5-10"><span class="s2">Rick: (stumbles in drunkenly, and turns on the lights) Morty! You gotta come on. You got--... you gotta come with me.</span>
</span><span id="__span-5-11"><span class="s2">Morty: (rubs his eyes) What, Rick? What&#39;s going on?</span>
</span><span id="__span-5-12"><span class="s2">Rick: I got a surprise for you, Morty.</span>
</span><span id="__span-5-13"><span class="s2">Morty: It&#39;s the middle of the night. What are you talking about?</span>
</span><span id="__span-5-14"><span class="s2">Rick: (spills alcohol on Morty&#39;s bed) Come on, I got a surprise for you. (drags Morty by the ankle) Come on, hurry up. (pulls Morty out of his bed and into the hall)</span>
</span><span id="__span-5-15"><span class="s2">Morty: Ow! Ow! You&#39;re tugging me too hard!</span>
</span><span id="__span-5-16"><span class="s2">Rick: We gotta go, gotta get outta here, come on. Got a surprise for you Morty.</span>
</span><span id="__span-5-17"><span class="s2">&quot;&quot;&quot;</span>
</span><span id="__span-5-18">
</span><span id="__span-5-19">
</span><span id="__span-5-20"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-5-21"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_story</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">AsyncIterable</span><span class="p">[</span><span class="nb">str</span><span class="p">]:</span>
</span><span id="__span-5-22">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-5-23">        <span class="k">yield</span> <span class="n">line</span>
</span><span id="__span-5-24">
</span><span id="__span-5-25">
</span><span id="__span-5-26"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-async&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-5-27"><span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_async</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">str</span><span class="p">]:</span>
</span><span id="__span-5-28">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-5-29">        <span class="k">yield</span> <span class="n">line</span>
</span><span id="__span-5-30">
</span><span id="__span-5-31">
</span><span id="__span-5-32"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-annotation&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-5-33"><span class="hll"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_annotation</span><span class="p">():</span>
</span></span><span id="__span-5-34">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-5-35">        <span class="k">yield</span> <span class="n">line</span>
</span><span id="__span-5-36">
</span><span id="__span-5-37">
</span><span id="__span-5-38"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-async-no-annotation&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-5-39"><span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_async_no_annotation</span><span class="p">():</span>
</span><span id="__span-5-40">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-5-41">        <span class="k">yield</span> <span class="n">line</span>
</span><span id="__span-5-42">
</span><span id="__span-5-43">
</span><span id="__span-5-44"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-bytes&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-5-45"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_story_bytes</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">AsyncIterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-5-46">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-5-47">        <span class="k">yield</span> <span class="n">line</span><span class="o">.</span><span class="n">encode</span><span class="p">(</span><span class="s2">&quot;utf-8&quot;</span><span class="p">)</span>
</span><span id="__span-5-48">
</span><span id="__span-5-49">
</span><span id="__span-5-50"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-async-bytes&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-5-51"><span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_async_bytes</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-5-52">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-5-53">        <span class="k">yield</span> <span class="n">line</span><span class="o">.</span><span class="n">encode</span><span class="p">(</span><span class="s2">&quot;utf-8&quot;</span><span class="p">)</span>
</span><span id="__span-5-54">
</span><span id="__span-5-55">
</span><span id="__span-5-56"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-annotation-bytes&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-5-57"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_annotation_bytes</span><span class="p">():</span>
</span><span id="__span-5-58">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-5-59">        <span class="k">yield</span> <span class="n">line</span><span class="o">.</span><span class="n">encode</span><span class="p">(</span><span class="s2">&quot;utf-8&quot;</span><span class="p">)</span>
</span><span id="__span-5-60">
</span><span id="__span-5-61">
</span><span id="__span-5-62"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-async-no-annotation-bytes&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-5-63"><span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_async_no_annotation_bytes</span><span class="p">():</span>
</span><span id="__span-5-64">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-5-65">        <span class="k">yield</span> <span class="n">line</span><span class="o">.</span><span class="n">encode</span><span class="p">(</span><span class="s2">&quot;utf-8&quot;</span><span class="p">)</span>
</span></code></pre></div>
</div>
</div>
</div>
</details>
<p>This also means that with <code>StreamingResponse</code> you have the <strong>freedom</strong> and <strong>responsibility</strong> to produce and encode the data bytes exactly as you need them to be sent, independent of the type annotations. 🤓</p>
<h3 id="stream-bytes">Stream Bytes<a class="headerlink" href="#stream-bytes" title="Permanent link">&para;</a></h3>
<p>One of the main use cases would be to stream <code>bytes</code> instead of strings, you can of course do it.</p>
<div class="tabbed-set tabbed-alternate" data-tabs="7:1"><input checked="checked" id="__tabbed_7_1" name="__tabbed_7" type="radio" /><div class="tabbed-labels"><label for="__tabbed_7_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-6-1"><span class="c1"># Code above omitted 👆</span>
</span><span id="__span-6-2">
</span><span id="__span-6-3"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-bytes&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-6-4"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_story_bytes</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">AsyncIterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-6-5">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-6-6"><span class="hll">        <span class="k">yield</span> <span class="n">line</span><span class="o">.</span><span class="n">encode</span><span class="p">(</span><span class="s2">&quot;utf-8&quot;</span><span class="p">)</span>
</span></span><span id="__span-6-7">
</span><span id="__span-6-8"><span class="c1"># Code below omitted 👇</span>
</span></code></pre></div>
</div>
</div>
</div>
<details>
<summary>👀 Full file preview</summary>
<div class="tabbed-set tabbed-alternate" data-tabs="8:1"><input checked="checked" id="__tabbed_8_1" name="__tabbed_8" type="radio" /><div class="tabbed-labels"><label for="__tabbed_8_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-7-1"><span class="kn">from</span><span class="w"> </span><span class="nn">collections.abc</span><span class="w"> </span><span class="kn">import</span> <span class="n">AsyncIterable</span><span class="p">,</span> <span class="n">Iterable</span>
</span><span id="__span-7-2">
</span><span id="__span-7-3"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-7-4"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">StreamingResponse</span>
</span><span id="__span-7-5">
</span><span id="__span-7-6"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-7-7">
</span><span id="__span-7-8">
</span><span id="__span-7-9"><span class="n">message</span> <span class="o">=</span> <span class="s2">&quot;&quot;&quot;</span>
</span><span id="__span-7-10"><span class="s2">Rick: (stumbles in drunkenly, and turns on the lights) Morty! You gotta come on. You got--... you gotta come with me.</span>
</span><span id="__span-7-11"><span class="s2">Morty: (rubs his eyes) What, Rick? What&#39;s going on?</span>
</span><span id="__span-7-12"><span class="s2">Rick: I got a surprise for you, Morty.</span>
</span><span id="__span-7-13"><span class="s2">Morty: It&#39;s the middle of the night. What are you talking about?</span>
</span><span id="__span-7-14"><span class="s2">Rick: (spills alcohol on Morty&#39;s bed) Come on, I got a surprise for you. (drags Morty by the ankle) Come on, hurry up. (pulls Morty out of his bed and into the hall)</span>
</span><span id="__span-7-15"><span class="s2">Morty: Ow! Ow! You&#39;re tugging me too hard!</span>
</span><span id="__span-7-16"><span class="s2">Rick: We gotta go, gotta get outta here, come on. Got a surprise for you Morty.</span>
</span><span id="__span-7-17"><span class="s2">&quot;&quot;&quot;</span>
</span><span id="__span-7-18">
</span><span id="__span-7-19">
</span><span id="__span-7-20"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-7-21"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_story</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">AsyncIterable</span><span class="p">[</span><span class="nb">str</span><span class="p">]:</span>
</span><span id="__span-7-22">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-7-23">        <span class="k">yield</span> <span class="n">line</span>
</span><span id="__span-7-24">
</span><span id="__span-7-25">
</span><span id="__span-7-26"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-async&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-7-27"><span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_async</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">str</span><span class="p">]:</span>
</span><span id="__span-7-28">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-7-29">        <span class="k">yield</span> <span class="n">line</span>
</span><span id="__span-7-30">
</span><span id="__span-7-31">
</span><span id="__span-7-32"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-annotation&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-7-33"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_annotation</span><span class="p">():</span>
</span><span id="__span-7-34">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-7-35">        <span class="k">yield</span> <span class="n">line</span>
</span><span id="__span-7-36">
</span><span id="__span-7-37">
</span><span id="__span-7-38"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-async-no-annotation&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-7-39"><span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_async_no_annotation</span><span class="p">():</span>
</span><span id="__span-7-40">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-7-41">        <span class="k">yield</span> <span class="n">line</span>
</span><span id="__span-7-42">
</span><span id="__span-7-43">
</span><span id="__span-7-44"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-bytes&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-7-45"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_story_bytes</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">AsyncIterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-7-46">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-7-47"><span class="hll">        <span class="k">yield</span> <span class="n">line</span><span class="o">.</span><span class="n">encode</span><span class="p">(</span><span class="s2">&quot;utf-8&quot;</span><span class="p">)</span>
</span></span><span id="__span-7-48">
</span><span id="__span-7-49">
</span><span id="__span-7-50"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-async-bytes&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-7-51"><span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_async_bytes</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-7-52">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-7-53">        <span class="k">yield</span> <span class="n">line</span><span class="o">.</span><span class="n">encode</span><span class="p">(</span><span class="s2">&quot;utf-8&quot;</span><span class="p">)</span>
</span><span id="__span-7-54">
</span><span id="__span-7-55">
</span><span id="__span-7-56"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-annotation-bytes&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-7-57"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_annotation_bytes</span><span class="p">():</span>
</span><span id="__span-7-58">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-7-59">        <span class="k">yield</span> <span class="n">line</span><span class="o">.</span><span class="n">encode</span><span class="p">(</span><span class="s2">&quot;utf-8&quot;</span><span class="p">)</span>
</span><span id="__span-7-60">
</span><span id="__span-7-61">
</span><span id="__span-7-62"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/story/stream-no-async-no-annotation-bytes&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">StreamingResponse</span><span class="p">)</span>
</span><span id="__span-7-63"><span class="k">def</span><span class="w"> </span><span class="nf">stream_story_no_async_no_annotation_bytes</span><span class="p">():</span>
</span><span id="__span-7-64">    <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">message</span><span class="o">.</span><span class="n">splitlines</span><span class="p">():</span>
</span><span id="__span-7-65">        <span class="k">yield</span> <span class="n">line</span><span class="o">.</span><span class="n">encode</span><span class="p">(</span><span class="s2">&quot;utf-8&quot;</span><span class="p">)</span>
</span></code></pre></div>
</div>
</div>
</div>
</details>
<h2 id="a-custom-pngstreamingresponse">A Custom <code>PNGStreamingResponse</code><a class="headerlink" href="#a-custom-pngstreamingresponse" title="Permanent link">&para;</a></h2>
<p>In the examples above, the data bytes were streamed, but the response didn't have a <code>Content-Type</code> header, so the client didn't know what type of data it was receiving.</p>
<p>You can create a custom sub-class of <code>StreamingResponse</code> that sets the <code>Content-Type</code> header to the type of data you're streaming.</p>
<p>For example, you can create a <code>PNGStreamingResponse</code> that sets the <code>Content-Type</code> header to <code>image/png</code> using the <code>media_type</code> attribute:</p>
<div class="tabbed-set tabbed-alternate" data-tabs="9:1"><input checked="checked" id="__tabbed_9_1" name="__tabbed_9" type="radio" /><div class="tabbed-labels"><label for="__tabbed_9_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-8-1"><span class="c1"># Code above omitted 👆</span>
</span><span id="__span-8-2">
</span><span id="__span-8-3"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">StreamingResponse</span>
</span><span id="__span-8-4">
</span><span id="__span-8-5"><span class="c1"># Code here omitted 👈</span>
</span><span id="__span-8-6">
</span><span id="__span-8-7"><span class="k">class</span><span class="w"> </span><span class="nc">PNGStreamingResponse</span><span class="p">(</span><span class="n">StreamingResponse</span><span class="p">):</span>
</span><span id="__span-8-8"><span class="hll">    <span class="n">media_type</span> <span class="o">=</span> <span class="s2">&quot;image/png&quot;</span>
</span></span><span id="__span-8-9">
</span><span id="__span-8-10"><span class="c1"># Code below omitted 👇</span>
</span></code></pre></div>
</div>
</div>
</div>
<details>
<summary>👀 Full file preview</summary>
<div class="tabbed-set tabbed-alternate" data-tabs="10:1"><input checked="checked" id="__tabbed_10_1" name="__tabbed_10" type="radio" /><div class="tabbed-labels"><label for="__tabbed_10_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-9-1"><span class="kn">import</span><span class="w"> </span><span class="nn">base64</span>
</span><span id="__span-9-2"><span class="kn">from</span><span class="w"> </span><span class="nn">collections.abc</span><span class="w"> </span><span class="kn">import</span> <span class="n">AsyncIterable</span><span class="p">,</span> <span class="n">Iterable</span>
</span><span id="__span-9-3"><span class="kn">from</span><span class="w"> </span><span class="nn">io</span><span class="w"> </span><span class="kn">import</span> <span class="n">BytesIO</span>
</span><span id="__span-9-4">
</span><span id="__span-9-5"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-9-6"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">StreamingResponse</span>
</span><span id="__span-9-7">
</span><span id="__span-9-8"><span class="n">image_base64</span> <span class="o">=</span> <span class="s2">&quot;iVBORw0KGgoAAAANSUhEUgAAAB0AAAAdCAYAAABWk2cPAAAAbnpUWHRSYXcgcHJvZmlsZSB0eXBlIGV4aWYAAHjadYzRDYAwCET/mcIRDoq0jGOiJm7g+NJK0vjhS4DjIEfHfZ20DKqSrrWZmyFQV5ctRMOLACxglNCcXk7zVqFzJzF8kV6R5vOJ97yVH78HjfYAtg0ged033ZgAAAoCaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8P3hwYWNrZXQgYmVnaW49Iu+7vyIgaWQ9Ilc1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCI/Pgo8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJYTVAgQ29yZSA0LjQuMC1FeGl2MiI+CiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiCiAgICB4bWxuczpleGlmPSJodHRwOi8vbnMuYWRvYmUuY29tL2V4aWYvMS4wLyIKICAgIHhtbG5zOnRpZmY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vdGlmZi8xLjAvIgogICBleGlmOlBpeGVsWERpbWVuc2lvbj0iMjkiCiAgIGV4aWY6UGl4ZWxZRGltZW5zaW9uPSIyOSIKICAgdGlmZjpJbWFnZVdpZHRoPSIyOSIKICAgdGlmZjpJbWFnZUxlbmd0aD0iMjkiCiAgIHRpZmY6T3JpZW50YXRpb249IjEiLz4KIDwvcmRmOlJERj4KPC94OnhtcG1ldGE+CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAKPD94cGFja2V0IGVuZD0idyI/PnQkBZAAAAAEc0JJVAgICAh8CGSIAAABoklEQVRIx8VXwY7FIAjE5iXWU+P/f6RHPNW9LIaOoHYP+0yMShVkwNGG1lqjfy4HfaF0oyEEt+oSQqBaa//m9Wd6PlqhhbRMDiEQM3e59FNKw5qZHpnQfuPaW6lazsztvu/eElFj5j63lNLlMz2ttbZtVMu1MTGo5Sujn93gMzOllKiUQjHGB9QxxneZhJ5iwZ1rL2fwenoGeL0q3wVGhBPHMz0PeFccIfASEeWcO8xEROd50q6eAV6s1s5XXoncas1EKqVQznnwUBdJJmm1l3hmmdlOMrGO8Vl5gZ56Y0y8IZF0BuqkQWM4B6HXrRCKa1SEqyzEo7KK59RT/VHDjX3ZvSefeW3CO6O6vsiA1NrwVkxxAcYTCcHyTjZmJd00pugBQoTnzjvn+kzLBh9GtRDjhleZFwbx3kugP3GvFzdkqRlbDYw0u/HxKjuOw2QxZCGL5V5f4l7cd6qsffUa1DcLM9N1XcTMvep5ul1e4jNPtZfWGIkE6dI8MquXg/dS2CGVJQ2ushd5GmlxFdOw+1tRa32MY4zDQ9yaZ60J3/iX+QG4U3qGrFHmswAAAABJRU5ErkJggg==&quot;</span>
</span><span id="__span-9-9"><span class="n">binary_image</span> <span class="o">=</span> <span class="n">base64</span><span class="o">.</span><span class="n">b64decode</span><span class="p">(</span><span class="n">image_base64</span><span class="p">)</span>
</span><span id="__span-9-10">
</span><span id="__span-9-11">
</span><span id="__span-9-12"><span class="k">def</span><span class="w"> </span><span class="nf">read_image</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">BytesIO</span><span class="p">:</span>
</span><span id="__span-9-13">    <span class="k">return</span> <span class="n">BytesIO</span><span class="p">(</span><span class="n">binary_image</span><span class="p">)</span>
</span><span id="__span-9-14">
</span><span id="__span-9-15">
</span><span id="__span-9-16"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-9-17">
</span><span id="__span-9-18">
</span><span id="__span-9-19"><span class="k">class</span><span class="w"> </span><span class="nc">PNGStreamingResponse</span><span class="p">(</span><span class="n">StreamingResponse</span><span class="p">):</span>
</span><span id="__span-9-20"><span class="hll">    <span class="n">media_type</span> <span class="o">=</span> <span class="s2">&quot;image/png&quot;</span>
</span></span><span id="__span-9-21">
</span><span id="__span-9-22">
</span><span id="__span-9-23"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-9-24"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_image</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">AsyncIterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-9-25">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-9-26">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-9-27">            <span class="k">yield</span> <span class="n">chunk</span>
</span><span id="__span-9-28">
</span><span id="__span-9-29">
</span><span id="__span-9-30"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-async&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-9-31"><span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_async</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-9-32">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-9-33">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-9-34">            <span class="k">yield</span> <span class="n">chunk</span>
</span><span id="__span-9-35">
</span><span id="__span-9-36">
</span><span id="__span-9-37"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-async-yield-from&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-9-38"><span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_async_yield_from</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-9-39">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-9-40">        <span class="k">yield from</span> <span class="n">image_file</span>
</span><span id="__span-9-41">
</span><span id="__span-9-42">
</span><span id="__span-9-43"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-annotation&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-9-44"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_annotation</span><span class="p">():</span>
</span><span id="__span-9-45">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-9-46">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-9-47">            <span class="k">yield</span> <span class="n">chunk</span>
</span><span id="__span-9-48">
</span><span id="__span-9-49">
</span><span id="__span-9-50"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-async-no-annotation&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-9-51"><span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_async_no_annotation</span><span class="p">():</span>
</span><span id="__span-9-52">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-9-53">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-9-54">            <span class="k">yield</span> <span class="n">chunk</span>
</span></code></pre></div>
</div>
</div>
</div>
</details>
<p>Then you can use this new class in <code>response_class=PNGStreamingResponse</code> in your <em>path operation function</em>:</p>
<div class="tabbed-set tabbed-alternate" data-tabs="11:1"><input checked="checked" id="__tabbed_11_1" name="__tabbed_11" type="radio" /><div class="tabbed-labels"><label for="__tabbed_11_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-10-1"><span class="c1"># Code above omitted 👆</span>
</span><span id="__span-10-2">
</span><span id="__span-10-3"><span class="hll"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span></span><span id="__span-10-4"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_image</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">AsyncIterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-10-5">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-10-6">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-10-7">            <span class="k">yield</span> <span class="n">chunk</span>
</span><span id="__span-10-8">
</span><span id="__span-10-9"><span class="c1"># Code below omitted 👇</span>
</span></code></pre></div>
</div>
</div>
</div>
<details>
<summary>👀 Full file preview</summary>
<div class="tabbed-set tabbed-alternate" data-tabs="12:1"><input checked="checked" id="__tabbed_12_1" name="__tabbed_12" type="radio" /><div class="tabbed-labels"><label for="__tabbed_12_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-11-1"><span class="kn">import</span><span class="w"> </span><span class="nn">base64</span>
</span><span id="__span-11-2"><span class="kn">from</span><span class="w"> </span><span class="nn">collections.abc</span><span class="w"> </span><span class="kn">import</span> <span class="n">AsyncIterable</span><span class="p">,</span> <span class="n">Iterable</span>
</span><span id="__span-11-3"><span class="kn">from</span><span class="w"> </span><span class="nn">io</span><span class="w"> </span><span class="kn">import</span> <span class="n">BytesIO</span>
</span><span id="__span-11-4">
</span><span id="__span-11-5"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-11-6"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">StreamingResponse</span>
</span><span id="__span-11-7">
</span><span id="__span-11-8"><span class="n">image_base64</span> <span class="o">=</span> <span class="s2">&quot;iVBORw0KGgoAAAANSUhEUgAAAB0AAAAdCAYAAABWk2cPAAAAbnpUWHRSYXcgcHJvZmlsZSB0eXBlIGV4aWYAAHjadYzRDYAwCET/mcIRDoq0jGOiJm7g+NJK0vjhS4DjIEfHfZ20DKqSrrWZmyFQV5ctRMOLACxglNCcXk7zVqFzJzF8kV6R5vOJ97yVH78HjfYAtg0ged033ZgAAAoCaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8P3hwYWNrZXQgYmVnaW49Iu+7vyIgaWQ9Ilc1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCI/Pgo8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJYTVAgQ29yZSA0LjQuMC1FeGl2MiI+CiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiCiAgICB4bWxuczpleGlmPSJodHRwOi8vbnMuYWRvYmUuY29tL2V4aWYvMS4wLyIKICAgIHhtbG5zOnRpZmY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vdGlmZi8xLjAvIgogICBleGlmOlBpeGVsWERpbWVuc2lvbj0iMjkiCiAgIGV4aWY6UGl4ZWxZRGltZW5zaW9uPSIyOSIKICAgdGlmZjpJbWFnZVdpZHRoPSIyOSIKICAgdGlmZjpJbWFnZUxlbmd0aD0iMjkiCiAgIHRpZmY6T3JpZW50YXRpb249IjEiLz4KIDwvcmRmOlJERj4KPC94OnhtcG1ldGE+CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAKPD94cGFja2V0IGVuZD0idyI/PnQkBZAAAAAEc0JJVAgICAh8CGSIAAABoklEQVRIx8VXwY7FIAjE5iXWU+P/f6RHPNW9LIaOoHYP+0yMShVkwNGG1lqjfy4HfaF0oyEEt+oSQqBaa//m9Wd6PlqhhbRMDiEQM3e59FNKw5qZHpnQfuPaW6lazsztvu/eElFj5j63lNLlMz2ttbZtVMu1MTGo5Sujn93gMzOllKiUQjHGB9QxxneZhJ5iwZ1rL2fwenoGeL0q3wVGhBPHMz0PeFccIfASEeWcO8xEROd50q6eAV6s1s5XXoncas1EKqVQznnwUBdJJmm1l3hmmdlOMrGO8Vl5gZ56Y0y8IZF0BuqkQWM4B6HXrRCKa1SEqyzEo7KK59RT/VHDjX3ZvSefeW3CO6O6vsiA1NrwVkxxAcYTCcHyTjZmJd00pugBQoTnzjvn+kzLBh9GtRDjhleZFwbx3kugP3GvFzdkqRlbDYw0u/HxKjuOw2QxZCGL5V5f4l7cd6qsffUa1DcLM9N1XcTMvep5ul1e4jNPtZfWGIkE6dI8MquXg/dS2CGVJQ2ushd5GmlxFdOw+1tRa32MY4zDQ9yaZ60J3/iX+QG4U3qGrFHmswAAAABJRU5ErkJggg==&quot;</span>
</span><span id="__span-11-9"><span class="n">binary_image</span> <span class="o">=</span> <span class="n">base64</span><span class="o">.</span><span class="n">b64decode</span><span class="p">(</span><span class="n">image_base64</span><span class="p">)</span>
</span><span id="__span-11-10">
</span><span id="__span-11-11">
</span><span id="__span-11-12"><span class="k">def</span><span class="w"> </span><span class="nf">read_image</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">BytesIO</span><span class="p">:</span>
</span><span id="__span-11-13">    <span class="k">return</span> <span class="n">BytesIO</span><span class="p">(</span><span class="n">binary_image</span><span class="p">)</span>
</span><span id="__span-11-14">
</span><span id="__span-11-15">
</span><span id="__span-11-16"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-11-17">
</span><span id="__span-11-18">
</span><span id="__span-11-19"><span class="k">class</span><span class="w"> </span><span class="nc">PNGStreamingResponse</span><span class="p">(</span><span class="n">StreamingResponse</span><span class="p">):</span>
</span><span id="__span-11-20">    <span class="n">media_type</span> <span class="o">=</span> <span class="s2">&quot;image/png&quot;</span>
</span><span id="__span-11-21">
</span><span id="__span-11-22">
</span><span id="__span-11-23"><span class="hll"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span></span><span id="__span-11-24"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_image</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">AsyncIterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-11-25">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-11-26">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-11-27">            <span class="k">yield</span> <span class="n">chunk</span>
</span><span id="__span-11-28">
</span><span id="__span-11-29">
</span><span id="__span-11-30"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-async&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-11-31"><span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_async</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-11-32">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-11-33">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-11-34">            <span class="k">yield</span> <span class="n">chunk</span>
</span><span id="__span-11-35">
</span><span id="__span-11-36">
</span><span id="__span-11-37"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-async-yield-from&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-11-38"><span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_async_yield_from</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-11-39">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-11-40">        <span class="k">yield from</span> <span class="n">image_file</span>
</span><span id="__span-11-41">
</span><span id="__span-11-42">
</span><span id="__span-11-43"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-annotation&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-11-44"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_annotation</span><span class="p">():</span>
</span><span id="__span-11-45">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-11-46">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-11-47">            <span class="k">yield</span> <span class="n">chunk</span>
</span><span id="__span-11-48">
</span><span id="__span-11-49">
</span><span id="__span-11-50"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-async-no-annotation&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-11-51"><span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_async_no_annotation</span><span class="p">():</span>
</span><span id="__span-11-52">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-11-53">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-11-54">            <span class="k">yield</span> <span class="n">chunk</span>
</span></code></pre></div>
</div>
</div>
</div>
</details>
<h3 id="simulate-a-file">Simulate a File<a class="headerlink" href="#simulate-a-file" title="Permanent link">&para;</a></h3>
<p>In this example, we are simulating a file with <code>io.BytesIO</code>, which is a file-like object that lives only in memory, but lets us use the same interface.</p>
<p>For example, we can iterate over it to consume its contents, as we could with a file.</p>
<div class="tabbed-set tabbed-alternate" data-tabs="13:1"><input checked="checked" id="__tabbed_13_1" name="__tabbed_13" type="radio" /><div class="tabbed-labels"><label for="__tabbed_13_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-12-1"><span class="kn">import</span><span class="w"> </span><span class="nn">base64</span>
</span><span id="__span-12-2"><span class="kn">from</span><span class="w"> </span><span class="nn">collections.abc</span><span class="w"> </span><span class="kn">import</span> <span class="n">AsyncIterable</span><span class="p">,</span> <span class="n">Iterable</span>
</span><span id="__span-12-3"><span class="hll"><span class="kn">from</span><span class="w"> </span><span class="nn">io</span><span class="w"> </span><span class="kn">import</span> <span class="n">BytesIO</span>
</span></span><span id="__span-12-4">
</span><span id="__span-12-5"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-12-6"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">StreamingResponse</span>
</span><span id="__span-12-7">
</span><span id="__span-12-8"><span class="n">image_base64</span> <span class="o">=</span> <span class="s2">&quot;iVBORw0KGgoAAAANSUhEUgAAAB0AAAAdCAYAAABWk2cPAAAAbnpUWHRSYXcgcHJvZmlsZSB0eXBlIGV4aWYAAHjadYzRDYAwCET/mcIRDoq0jGOiJm7g+NJK0vjhS4DjIEfHfZ20DKqSrrWZmyFQV5ctRMOLACxglNCcXk7zVqFzJzF8kV6R5vOJ97yVH78HjfYAtg0ged033ZgAAAoCaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8P3hwYWNrZXQgYmVnaW49Iu+7vyIgaWQ9Ilc1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCI/Pgo8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJYTVAgQ29yZSA0LjQuMC1FeGl2MiI+CiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiCiAgICB4bWxuczpleGlmPSJodHRwOi8vbnMuYWRvYmUuY29tL2V4aWYvMS4wLyIKICAgIHhtbG5zOnRpZmY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vdGlmZi8xLjAvIgogICBleGlmOlBpeGVsWERpbWVuc2lvbj0iMjkiCiAgIGV4aWY6UGl4ZWxZRGltZW5zaW9uPSIyOSIKICAgdGlmZjpJbWFnZVdpZHRoPSIyOSIKICAgdGlmZjpJbWFnZUxlbmd0aD0iMjkiCiAgIHRpZmY6T3JpZW50YXRpb249IjEiLz4KIDwvcmRmOlJERj4KPC94OnhtcG1ldGE+CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAKPD94cGFja2V0IGVuZD0idyI/PnQkBZAAAAAEc0JJVAgICAh8CGSIAAABoklEQVRIx8VXwY7FIAjE5iXWU+P/f6RHPNW9LIaOoHYP+0yMShVkwNGG1lqjfy4HfaF0oyEEt+oSQqBaa//m9Wd6PlqhhbRMDiEQM3e59FNKw5qZHpnQfuPaW6lazsztvu/eElFj5j63lNLlMz2ttbZtVMu1MTGo5Sujn93gMzOllKiUQjHGB9QxxneZhJ5iwZ1rL2fwenoGeL0q3wVGhBPHMz0PeFccIfASEeWcO8xEROd50q6eAV6s1s5XXoncas1EKqVQznnwUBdJJmm1l3hmmdlOMrGO8Vl5gZ56Y0y8IZF0BuqkQWM4B6HXrRCKa1SEqyzEo7KK59RT/VHDjX3ZvSefeW3CO6O6vsiA1NrwVkxxAcYTCcHyTjZmJd00pugBQoTnzjvn+kzLBh9GtRDjhleZFwbx3kugP3GvFzdkqRlbDYw0u/HxKjuOw2QxZCGL5V5f4l7cd6qsffUa1DcLM9N1XcTMvep5ul1e4jNPtZfWGIkE6dI8MquXg/dS2CGVJQ2ushd5GmlxFdOw+1tRa32MY4zDQ9yaZ60J3/iX+QG4U3qGrFHmswAAAABJRU5ErkJggg==&quot;</span>
</span><span id="__span-12-9"><span class="n">binary_image</span> <span class="o">=</span> <span class="n">base64</span><span class="o">.</span><span class="n">b64decode</span><span class="p">(</span><span class="n">image_base64</span><span class="p">)</span>
</span><span id="__span-12-10">
</span><span id="__span-12-11">
</span><span id="__span-12-12"><span class="hll"><span class="k">def</span><span class="w"> </span><span class="nf">read_image</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">BytesIO</span><span class="p">:</span>
</span></span><span id="__span-12-13"><span class="hll">    <span class="k">return</span> <span class="n">BytesIO</span><span class="p">(</span><span class="n">binary_image</span><span class="p">)</span>
</span></span><span id="__span-12-14">
</span><span id="__span-12-15">
</span><span id="__span-12-16"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-12-17">
</span><span id="__span-12-18">
</span><span id="__span-12-19"><span class="k">class</span><span class="w"> </span><span class="nc">PNGStreamingResponse</span><span class="p">(</span><span class="n">StreamingResponse</span><span class="p">):</span>
</span><span id="__span-12-20">    <span class="n">media_type</span> <span class="o">=</span> <span class="s2">&quot;image/png&quot;</span>
</span><span id="__span-12-21">
</span><span id="__span-12-22">
</span><span id="__span-12-23"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-12-24"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_image</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">AsyncIterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-12-25"><span class="hll">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span></span><span id="__span-12-26">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-12-27">            <span class="k">yield</span> <span class="n">chunk</span>
</span><span id="__span-12-28">
</span><span id="__span-12-29"><span class="c1"># Code below omitted 👇</span>
</span></code></pre></div>
</div>
</div>
</div>
<details>
<summary>👀 Full file preview</summary>
<div class="tabbed-set tabbed-alternate" data-tabs="14:1"><input checked="checked" id="__tabbed_14_1" name="__tabbed_14" type="radio" /><div class="tabbed-labels"><label for="__tabbed_14_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-13-1"><span class="kn">import</span><span class="w"> </span><span class="nn">base64</span>
</span><span id="__span-13-2"><span class="kn">from</span><span class="w"> </span><span class="nn">collections.abc</span><span class="w"> </span><span class="kn">import</span> <span class="n">AsyncIterable</span><span class="p">,</span> <span class="n">Iterable</span>
</span><span id="__span-13-3"><span class="hll"><span class="kn">from</span><span class="w"> </span><span class="nn">io</span><span class="w"> </span><span class="kn">import</span> <span class="n">BytesIO</span>
</span></span><span id="__span-13-4">
</span><span id="__span-13-5"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-13-6"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">StreamingResponse</span>
</span><span id="__span-13-7">
</span><span id="__span-13-8"><span class="n">image_base64</span> <span class="o">=</span> <span class="s2">&quot;iVBORw0KGgoAAAANSUhEUgAAAB0AAAAdCAYAAABWk2cPAAAAbnpUWHRSYXcgcHJvZmlsZSB0eXBlIGV4aWYAAHjadYzRDYAwCET/mcIRDoq0jGOiJm7g+NJK0vjhS4DjIEfHfZ20DKqSrrWZmyFQV5ctRMOLACxglNCcXk7zVqFzJzF8kV6R5vOJ97yVH78HjfYAtg0ged033ZgAAAoCaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8P3hwYWNrZXQgYmVnaW49Iu+7vyIgaWQ9Ilc1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCI/Pgo8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJYTVAgQ29yZSA0LjQuMC1FeGl2MiI+CiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiCiAgICB4bWxuczpleGlmPSJodHRwOi8vbnMuYWRvYmUuY29tL2V4aWYvMS4wLyIKICAgIHhtbG5zOnRpZmY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vdGlmZi8xLjAvIgogICBleGlmOlBpeGVsWERpbWVuc2lvbj0iMjkiCiAgIGV4aWY6UGl4ZWxZRGltZW5zaW9uPSIyOSIKICAgdGlmZjpJbWFnZVdpZHRoPSIyOSIKICAgdGlmZjpJbWFnZUxlbmd0aD0iMjkiCiAgIHRpZmY6T3JpZW50YXRpb249IjEiLz4KIDwvcmRmOlJERj4KPC94OnhtcG1ldGE+CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAKPD94cGFja2V0IGVuZD0idyI/PnQkBZAAAAAEc0JJVAgICAh8CGSIAAABoklEQVRIx8VXwY7FIAjE5iXWU+P/f6RHPNW9LIaOoHYP+0yMShVkwNGG1lqjfy4HfaF0oyEEt+oSQqBaa//m9Wd6PlqhhbRMDiEQM3e59FNKw5qZHpnQfuPaW6lazsztvu/eElFj5j63lNLlMz2ttbZtVMu1MTGo5Sujn93gMzOllKiUQjHGB9QxxneZhJ5iwZ1rL2fwenoGeL0q3wVGhBPHMz0PeFccIfASEeWcO8xEROd50q6eAV6s1s5XXoncas1EKqVQznnwUBdJJmm1l3hmmdlOMrGO8Vl5gZ56Y0y8IZF0BuqkQWM4B6HXrRCKa1SEqyzEo7KK59RT/VHDjX3ZvSefeW3CO6O6vsiA1NrwVkxxAcYTCcHyTjZmJd00pugBQoTnzjvn+kzLBh9GtRDjhleZFwbx3kugP3GvFzdkqRlbDYw0u/HxKjuOw2QxZCGL5V5f4l7cd6qsffUa1DcLM9N1XcTMvep5ul1e4jNPtZfWGIkE6dI8MquXg/dS2CGVJQ2ushd5GmlxFdOw+1tRa32MY4zDQ9yaZ60J3/iX+QG4U3qGrFHmswAAAABJRU5ErkJggg==&quot;</span>
</span><span id="__span-13-9"><span class="n">binary_image</span> <span class="o">=</span> <span class="n">base64</span><span class="o">.</span><span class="n">b64decode</span><span class="p">(</span><span class="n">image_base64</span><span class="p">)</span>
</span><span id="__span-13-10">
</span><span id="__span-13-11">
</span><span id="__span-13-12"><span class="hll"><span class="k">def</span><span class="w"> </span><span class="nf">read_image</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">BytesIO</span><span class="p">:</span>
</span></span><span id="__span-13-13"><span class="hll">    <span class="k">return</span> <span class="n">BytesIO</span><span class="p">(</span><span class="n">binary_image</span><span class="p">)</span>
</span></span><span id="__span-13-14">
</span><span id="__span-13-15">
</span><span id="__span-13-16"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-13-17">
</span><span id="__span-13-18">
</span><span id="__span-13-19"><span class="k">class</span><span class="w"> </span><span class="nc">PNGStreamingResponse</span><span class="p">(</span><span class="n">StreamingResponse</span><span class="p">):</span>
</span><span id="__span-13-20">    <span class="n">media_type</span> <span class="o">=</span> <span class="s2">&quot;image/png&quot;</span>
</span><span id="__span-13-21">
</span><span id="__span-13-22">
</span><span id="__span-13-23"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-13-24"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_image</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">AsyncIterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-13-25"><span class="hll">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span></span><span id="__span-13-26">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-13-27">            <span class="k">yield</span> <span class="n">chunk</span>
</span><span id="__span-13-28">
</span><span id="__span-13-29">
</span><span id="__span-13-30"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-async&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-13-31"><span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_async</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-13-32">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-13-33">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-13-34">            <span class="k">yield</span> <span class="n">chunk</span>
</span><span id="__span-13-35">
</span><span id="__span-13-36">
</span><span id="__span-13-37"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-async-yield-from&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-13-38"><span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_async_yield_from</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-13-39">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-13-40">        <span class="k">yield from</span> <span class="n">image_file</span>
</span><span id="__span-13-41">
</span><span id="__span-13-42">
</span><span id="__span-13-43"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-annotation&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-13-44"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_annotation</span><span class="p">():</span>
</span><span id="__span-13-45">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-13-46">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-13-47">            <span class="k">yield</span> <span class="n">chunk</span>
</span><span id="__span-13-48">
</span><span id="__span-13-49">
</span><span id="__span-13-50"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-async-no-annotation&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-13-51"><span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_async_no_annotation</span><span class="p">():</span>
</span><span id="__span-13-52">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-13-53">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-13-54">            <span class="k">yield</span> <span class="n">chunk</span>
</span></code></pre></div>
</div>
</div>
</div>
</details>
<div class="admonition note">
<p class="admonition-title">Technical Details</p>
<p>The other two variables, <code>image_base64</code> and <code>binary_image</code>, are an image encoded in Base64, and then converted to bytes, to then pass it to <code>io.BytesIO</code>.</p>
<p>Only so that it can live in the same file for this example and you can copy it and run it as is. 🥚</p>
</div>
<p>By using a <code>with</code> block, we make sure that the file-like object is closed after the generator function (the function with <code>yield</code>) is done. So, after it finishes sending the response.</p>
<p>It wouldn't be that important in this specific example because it's a fake in-memory file (with <code>io.BytesIO</code>), but with a real file, it would be important to make sure the file is closed after the work with it is done.</p>
<h3 id="files-and-async">Files and Async<a class="headerlink" href="#files-and-async" title="Permanent link">&para;</a></h3>
<p>In most cases, file-like objects are not compatible with async and await by default.</p>
<p>For example, they don't have an <code>await file.read()</code>, or <code>async for chunk in file</code>.</p>
<p>And in many cases, reading them would be a blocking operation (that could block the event loop), because they are read from disk or from the network.</p>
<div class="admonition note">
<p class="admonition-title">Note</p>
<p>The example above is actually an exception, because the <code>io.BytesIO</code> object is already in memory, so reading it won't block anything.</p>
<p>But in many cases reading a file or a file-like object would block.</p>
</div>
<p>To avoid blocking the event loop, you can simply declare the <em>path operation function</em> with regular <code>def</code> instead of <code>async def</code>, that way FastAPI will run it on a threadpool worker, to avoid blocking the main loop.</p>
<div class="tabbed-set tabbed-alternate" data-tabs="15:1"><input checked="checked" id="__tabbed_15_1" name="__tabbed_15" type="radio" /><div class="tabbed-labels"><label for="__tabbed_15_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-14-1"><span class="c1"># Code above omitted 👆</span>
</span><span id="__span-14-2">
</span><span id="__span-14-3"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-async&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-14-4"><span class="hll"><span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_async</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span></span><span id="__span-14-5">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-14-6">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-14-7">            <span class="k">yield</span> <span class="n">chunk</span>
</span><span id="__span-14-8">
</span><span id="__span-14-9"><span class="c1"># Code below omitted 👇</span>
</span></code></pre></div>
</div>
</div>
</div>
<details>
<summary>👀 Full file preview</summary>
<div class="tabbed-set tabbed-alternate" data-tabs="16:1"><input checked="checked" id="__tabbed_16_1" name="__tabbed_16" type="radio" /><div class="tabbed-labels"><label for="__tabbed_16_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-15-1"><span class="kn">import</span><span class="w"> </span><span class="nn">base64</span>
</span><span id="__span-15-2"><span class="kn">from</span><span class="w"> </span><span class="nn">collections.abc</span><span class="w"> </span><span class="kn">import</span> <span class="n">AsyncIterable</span><span class="p">,</span> <span class="n">Iterable</span>
</span><span id="__span-15-3"><span class="kn">from</span><span class="w"> </span><span class="nn">io</span><span class="w"> </span><span class="kn">import</span> <span class="n">BytesIO</span>
</span><span id="__span-15-4">
</span><span id="__span-15-5"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-15-6"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">StreamingResponse</span>
</span><span id="__span-15-7">
</span><span id="__span-15-8"><span class="n">image_base64</span> <span class="o">=</span> <span class="s2">&quot;iVBORw0KGgoAAAANSUhEUgAAAB0AAAAdCAYAAABWk2cPAAAAbnpUWHRSYXcgcHJvZmlsZSB0eXBlIGV4aWYAAHjadYzRDYAwCET/mcIRDoq0jGOiJm7g+NJK0vjhS4DjIEfHfZ20DKqSrrWZmyFQV5ctRMOLACxglNCcXk7zVqFzJzF8kV6R5vOJ97yVH78HjfYAtg0ged033ZgAAAoCaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8P3hwYWNrZXQgYmVnaW49Iu+7vyIgaWQ9Ilc1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCI/Pgo8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJYTVAgQ29yZSA0LjQuMC1FeGl2MiI+CiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiCiAgICB4bWxuczpleGlmPSJodHRwOi8vbnMuYWRvYmUuY29tL2V4aWYvMS4wLyIKICAgIHhtbG5zOnRpZmY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vdGlmZi8xLjAvIgogICBleGlmOlBpeGVsWERpbWVuc2lvbj0iMjkiCiAgIGV4aWY6UGl4ZWxZRGltZW5zaW9uPSIyOSIKICAgdGlmZjpJbWFnZVdpZHRoPSIyOSIKICAgdGlmZjpJbWFnZUxlbmd0aD0iMjkiCiAgIHRpZmY6T3JpZW50YXRpb249IjEiLz4KIDwvcmRmOlJERj4KPC94OnhtcG1ldGE+CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAKPD94cGFja2V0IGVuZD0idyI/PnQkBZAAAAAEc0JJVAgICAh8CGSIAAABoklEQVRIx8VXwY7FIAjE5iXWU+P/f6RHPNW9LIaOoHYP+0yMShVkwNGG1lqjfy4HfaF0oyEEt+oSQqBaa//m9Wd6PlqhhbRMDiEQM3e59FNKw5qZHpnQfuPaW6lazsztvu/eElFj5j63lNLlMz2ttbZtVMu1MTGo5Sujn93gMzOllKiUQjHGB9QxxneZhJ5iwZ1rL2fwenoGeL0q3wVGhBPHMz0PeFccIfASEeWcO8xEROd50q6eAV6s1s5XXoncas1EKqVQznnwUBdJJmm1l3hmmdlOMrGO8Vl5gZ56Y0y8IZF0BuqkQWM4B6HXrRCKa1SEqyzEo7KK59RT/VHDjX3ZvSefeW3CO6O6vsiA1NrwVkxxAcYTCcHyTjZmJd00pugBQoTnzjvn+kzLBh9GtRDjhleZFwbx3kugP3GvFzdkqRlbDYw0u/HxKjuOw2QxZCGL5V5f4l7cd6qsffUa1DcLM9N1XcTMvep5ul1e4jNPtZfWGIkE6dI8MquXg/dS2CGVJQ2ushd5GmlxFdOw+1tRa32MY4zDQ9yaZ60J3/iX+QG4U3qGrFHmswAAAABJRU5ErkJggg==&quot;</span>
</span><span id="__span-15-9"><span class="n">binary_image</span> <span class="o">=</span> <span class="n">base64</span><span class="o">.</span><span class="n">b64decode</span><span class="p">(</span><span class="n">image_base64</span><span class="p">)</span>
</span><span id="__span-15-10">
</span><span id="__span-15-11">
</span><span id="__span-15-12"><span class="k">def</span><span class="w"> </span><span class="nf">read_image</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">BytesIO</span><span class="p">:</span>
</span><span id="__span-15-13">    <span class="k">return</span> <span class="n">BytesIO</span><span class="p">(</span><span class="n">binary_image</span><span class="p">)</span>
</span><span id="__span-15-14">
</span><span id="__span-15-15">
</span><span id="__span-15-16"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-15-17">
</span><span id="__span-15-18">
</span><span id="__span-15-19"><span class="k">class</span><span class="w"> </span><span class="nc">PNGStreamingResponse</span><span class="p">(</span><span class="n">StreamingResponse</span><span class="p">):</span>
</span><span id="__span-15-20">    <span class="n">media_type</span> <span class="o">=</span> <span class="s2">&quot;image/png&quot;</span>
</span><span id="__span-15-21">
</span><span id="__span-15-22">
</span><span id="__span-15-23"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-15-24"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_image</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">AsyncIterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-15-25">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-15-26">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-15-27">            <span class="k">yield</span> <span class="n">chunk</span>
</span><span id="__span-15-28">
</span><span id="__span-15-29">
</span><span id="__span-15-30"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-async&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-15-31"><span class="hll"><span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_async</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span></span><span id="__span-15-32">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-15-33">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-15-34">            <span class="k">yield</span> <span class="n">chunk</span>
</span><span id="__span-15-35">
</span><span id="__span-15-36">
</span><span id="__span-15-37"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-async-yield-from&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-15-38"><span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_async_yield_from</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-15-39">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-15-40">        <span class="k">yield from</span> <span class="n">image_file</span>
</span><span id="__span-15-41">
</span><span id="__span-15-42">
</span><span id="__span-15-43"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-annotation&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-15-44"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_annotation</span><span class="p">():</span>
</span><span id="__span-15-45">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-15-46">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-15-47">            <span class="k">yield</span> <span class="n">chunk</span>
</span><span id="__span-15-48">
</span><span id="__span-15-49">
</span><span id="__span-15-50"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-async-no-annotation&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-15-51"><span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_async_no_annotation</span><span class="p">():</span>
</span><span id="__span-15-52">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-15-53">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-15-54">            <span class="k">yield</span> <span class="n">chunk</span>
</span></code></pre></div>
</div>
</div>
</div>
</details>
<div class="admonition tip">
<p class="admonition-title">Tip</p>
<p>If you need to call blocking code from inside of an async function, or an async function from inside of a blocking function, you could use <a href="https://asyncer.tiangolo.com">Asyncer</a>, a sibling library to FastAPI.</p>
</div>
<h3 id="yield-from"><code>yield from</code><a class="headerlink" href="#yield-from" title="Permanent link">&para;</a></h3>
<p>When you are iterating over something, like a file-like object, and then you are doing <code>yield</code> for each item, you could also use <code>yield from</code> to yield each item directly and skip the <code>for</code> loop.</p>
<p>This is not particular to FastAPI, it's just Python, but it's a nice trick to know. 😎</p>
<div class="tabbed-set tabbed-alternate" data-tabs="17:1"><input checked="checked" id="__tabbed_17_1" name="__tabbed_17" type="radio" /><div class="tabbed-labels"><label for="__tabbed_17_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-16-1"><span class="c1"># Code above omitted 👆</span>
</span><span id="__span-16-2">
</span><span id="__span-16-3"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-async-yield-from&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-16-4"><span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_async_yield_from</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-16-5">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-16-6"><span class="hll">        <span class="k">yield from</span> <span class="n">image_file</span>
</span></span><span id="__span-16-7">
</span><span id="__span-16-8"><span class="c1"># Code below omitted 👇</span>
</span></code></pre></div>
</div>
</div>
</div>
<details>
<summary>👀 Full file preview</summary>
<div class="tabbed-set tabbed-alternate" data-tabs="18:1"><input checked="checked" id="__tabbed_18_1" name="__tabbed_18" type="radio" /><div class="tabbed-labels"><label for="__tabbed_18_1">Python 3.10+</label></div>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="highlight"><pre><span></span><code><span id="__span-17-1"><span class="kn">import</span><span class="w"> </span><span class="nn">base64</span>
</span><span id="__span-17-2"><span class="kn">from</span><span class="w"> </span><span class="nn">collections.abc</span><span class="w"> </span><span class="kn">import</span> <span class="n">AsyncIterable</span><span class="p">,</span> <span class="n">Iterable</span>
</span><span id="__span-17-3"><span class="kn">from</span><span class="w"> </span><span class="nn">io</span><span class="w"> </span><span class="kn">import</span> <span class="n">BytesIO</span>
</span><span id="__span-17-4">
</span><span id="__span-17-5"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi</span><span class="w"> </span><span class="kn">import</span> <span class="n">FastAPI</span>
</span><span id="__span-17-6"><span class="kn">from</span><span class="w"> </span><span class="nn">fastapi.responses</span><span class="w"> </span><span class="kn">import</span> <span class="n">StreamingResponse</span>
</span><span id="__span-17-7">
</span><span id="__span-17-8"><span class="n">image_base64</span> <span class="o">=</span> <span class="s2">&quot;iVBORw0KGgoAAAANSUhEUgAAAB0AAAAdCAYAAABWk2cPAAAAbnpUWHRSYXcgcHJvZmlsZSB0eXBlIGV4aWYAAHjadYzRDYAwCET/mcIRDoq0jGOiJm7g+NJK0vjhS4DjIEfHfZ20DKqSrrWZmyFQV5ctRMOLACxglNCcXk7zVqFzJzF8kV6R5vOJ97yVH78HjfYAtg0ged033ZgAAAoCaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8P3hwYWNrZXQgYmVnaW49Iu+7vyIgaWQ9Ilc1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCI/Pgo8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJYTVAgQ29yZSA0LjQuMC1FeGl2MiI+CiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiCiAgICB4bWxuczpleGlmPSJodHRwOi8vbnMuYWRvYmUuY29tL2V4aWYvMS4wLyIKICAgIHhtbG5zOnRpZmY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vdGlmZi8xLjAvIgogICBleGlmOlBpeGVsWERpbWVuc2lvbj0iMjkiCiAgIGV4aWY6UGl4ZWxZRGltZW5zaW9uPSIyOSIKICAgdGlmZjpJbWFnZVdpZHRoPSIyOSIKICAgdGlmZjpJbWFnZUxlbmd0aD0iMjkiCiAgIHRpZmY6T3JpZW50YXRpb249IjEiLz4KIDwvcmRmOlJERj4KPC94OnhtcG1ldGE+CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAKPD94cGFja2V0IGVuZD0idyI/PnQkBZAAAAAEc0JJVAgICAh8CGSIAAABoklEQVRIx8VXwY7FIAjE5iXWU+P/f6RHPNW9LIaOoHYP+0yMShVkwNGG1lqjfy4HfaF0oyEEt+oSQqBaa//m9Wd6PlqhhbRMDiEQM3e59FNKw5qZHpnQfuPaW6lazsztvu/eElFj5j63lNLlMz2ttbZtVMu1MTGo5Sujn93gMzOllKiUQjHGB9QxxneZhJ5iwZ1rL2fwenoGeL0q3wVGhBPHMz0PeFccIfASEeWcO8xEROd50q6eAV6s1s5XXoncas1EKqVQznnwUBdJJmm1l3hmmdlOMrGO8Vl5gZ56Y0y8IZF0BuqkQWM4B6HXrRCKa1SEqyzEo7KK59RT/VHDjX3ZvSefeW3CO6O6vsiA1NrwVkxxAcYTCcHyTjZmJd00pugBQoTnzjvn+kzLBh9GtRDjhleZFwbx3kugP3GvFzdkqRlbDYw0u/HxKjuOw2QxZCGL5V5f4l7cd6qsffUa1DcLM9N1XcTMvep5ul1e4jNPtZfWGIkE6dI8MquXg/dS2CGVJQ2ushd5GmlxFdOw+1tRa32MY4zDQ9yaZ60J3/iX+QG4U3qGrFHmswAAAABJRU5ErkJggg==&quot;</span>
</span><span id="__span-17-9"><span class="n">binary_image</span> <span class="o">=</span> <span class="n">base64</span><span class="o">.</span><span class="n">b64decode</span><span class="p">(</span><span class="n">image_base64</span><span class="p">)</span>
</span><span id="__span-17-10">
</span><span id="__span-17-11">
</span><span id="__span-17-12"><span class="k">def</span><span class="w"> </span><span class="nf">read_image</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">BytesIO</span><span class="p">:</span>
</span><span id="__span-17-13">    <span class="k">return</span> <span class="n">BytesIO</span><span class="p">(</span><span class="n">binary_image</span><span class="p">)</span>
</span><span id="__span-17-14">
</span><span id="__span-17-15">
</span><span id="__span-17-16"><span class="n">app</span> <span class="o">=</span> <span class="n">FastAPI</span><span class="p">()</span>
</span><span id="__span-17-17">
</span><span id="__span-17-18">
</span><span id="__span-17-19"><span class="k">class</span><span class="w"> </span><span class="nc">PNGStreamingResponse</span><span class="p">(</span><span class="n">StreamingResponse</span><span class="p">):</span>
</span><span id="__span-17-20">    <span class="n">media_type</span> <span class="o">=</span> <span class="s2">&quot;image/png&quot;</span>
</span><span id="__span-17-21">
</span><span id="__span-17-22">
</span><span id="__span-17-23"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-17-24"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_image</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">AsyncIterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-17-25">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-17-26">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-17-27">            <span class="k">yield</span> <span class="n">chunk</span>
</span><span id="__span-17-28">
</span><span id="__span-17-29">
</span><span id="__span-17-30"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-async&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-17-31"><span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_async</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-17-32">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-17-33">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-17-34">            <span class="k">yield</span> <span class="n">chunk</span>
</span><span id="__span-17-35">
</span><span id="__span-17-36">
</span><span id="__span-17-37"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-async-yield-from&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-17-38"><span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_async_yield_from</span><span class="p">()</span> <span class="o">-&gt;</span> <span class="n">Iterable</span><span class="p">[</span><span class="nb">bytes</span><span class="p">]:</span>
</span><span id="__span-17-39">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-17-40"><span class="hll">        <span class="k">yield from</span> <span class="n">image_file</span>
</span></span><span id="__span-17-41">
</span><span id="__span-17-42">
</span><span id="__span-17-43"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-annotation&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-17-44"><span class="k">async</span> <span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_annotation</span><span class="p">():</span>
</span><span id="__span-17-45">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-17-46">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-17-47">            <span class="k">yield</span> <span class="n">chunk</span>
</span><span id="__span-17-48">
</span><span id="__span-17-49">
</span><span id="__span-17-50"><span class="nd">@app</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;/image/stream-no-async-no-annotation&quot;</span><span class="p">,</span> <span class="n">response_class</span><span class="o">=</span><span class="n">PNGStreamingResponse</span><span class="p">)</span>
</span><span id="__span-17-51"><span class="k">def</span><span class="w"> </span><span class="nf">stream_image_no_async_no_annotation</span><span class="p">():</span>
</span><span id="__span-17-52">    <span class="k">with</span> <span class="n">read_image</span><span class="p">()</span> <span class="k">as</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-17-53">        <span class="k">for</span> <span class="n">chunk</span> <span class="ow">in</span> <span class="n">image_file</span><span class="p">:</span>
</span><span id="__span-17-54">            <span class="k">yield</span> <span class="n">chunk</span>
</span></code></pre></div>
</div>
</div>
</div>
</details>















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
        
          
          <a href="../" class="md-footer__link md-footer__link--prev" aria-label="Previous: Advanced User Guide">
            <div class="md-footer__button md-icon">
              
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M20 11v2H8l5.5 5.5-1.42 1.42L4.16 12l7.92-7.92L13.5 5.5 8 11z"/></svg>
            </div>
            <div class="md-footer__title">
              <span class="md-footer__direction">
                Previous
              </span>
              <div class="md-ellipsis">
                Advanced User Guide
              </div>
            </div>
          </a>
        
        
          
          <a href="../path-operation-advanced-configuration/" class="md-footer__link md-footer__link--next" aria-label="Next: Path Operation Advanced Configuration">
            <div class="md-footer__title">
              <span class="md-footer__direction">
                Next
              </span>
              <div class="md-ellipsis">
                Path Operation Advanced Configuration
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