App({
  globalData: {
    userInfo: null,
    apiBaseUrl: 'http://localhost:8000',
    pendingQuestion: null
  },

  onLaunch() {
    console.log('智学助手小程序启动')

    // 检查用户信息
    wx.getSetting({
      success: (res) => {
        if (res.authSetting['scope.userInfo']) {
          wx.getUserInfo({
            success: (res) => {
              this.globalData.userInfo = res.userInfo
            }
          })
        }
      }
    })
  }
})
