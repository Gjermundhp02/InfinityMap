browser.tabs.create({
    url: "src/mypage.html"
})


browser.runtime.onMessage.addListener(message=>{
    console.log(message);
})

console.log("Extension loaded content script");