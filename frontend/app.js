App({
  globalData: {
    userInfo: null,
    apiBaseUrl: 'http://127.0.0.1:8000',
    pendingQuestion: null
  },

  onLaunch() {
    console.log('智学助手小程序启动')
    const savedApiBaseUrl = wx.getStorageSync('apiBaseUrl')
    if (savedApiBaseUrl) {
      this.globalData.apiBaseUrl = savedApiBaseUrl
    }

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
  },

  setApiBaseUrl(url) {
    const normalized = (url || '').trim().replace(/\/+$/, '')
    if (!normalized) {
      return
    }
    this.globalData.apiBaseUrl = normalized
    wx.setStorageSync('apiBaseUrl', normalized)
  },

  request(options) {
    const { url, fail, ...rest } = options
    return wx.request({
      url: this.globalData.apiBaseUrl + url,
      ...rest,
      fail: (error) => {
        if (typeof fail === 'function') {
          fail(error)
          return
        }
        wx.showToast({
          title: '无法连接后端，请检查地址配置',
          icon: 'none'
        })
      }
    })
  }
})
