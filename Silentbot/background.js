chrome.webNavigation.onBeforeNavigate.addListener(function(details) {
   if( details.frameId == 0 )
   chrome.tabs.get(details.tabId,function( tab ){
      var source_url = tab.url;
      var target_url = details.url;
      if( source_url != target_url )
      var xhr = new XMLHttpRequest();
      xhr.open("POST", 'http://www.askgraph.com/silent_bot_crawl', true);
      xhr.setRequestHeader("Content-type","application/x-www-form-urlencoded");
      xhr.send("source="+encodeURIComponent(source_url)+"&target="+encodeURIComponent(target_url));
   });
});
