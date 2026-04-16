const app = getApp()

Page({
  data: {
    recentFiles: []
  },

  onLoad() {
    this.loadRecentFiles()
  },

  onShow() {
    this.loadRecentFiles()
  },

  // 选择文件上传
  chooseFile() {
    wx.showActionSheet({
      itemList: ['从聊天记录选择', '从相册选择图片'],
      success: (res) => {
        if (res.tapIndex === 0) {
          this.chooseMessageFile()
        } else {
          this.chooseImage()
        }
      }
    })
  },

  // 从聊天记录选文件
  chooseMessageFile() {
    wx.chooseMessageFile({
      count: 1,
      type: 'file',
      extension: ['pdf', 'txt', 'doc', 'docx'],
      success: (res) => {
        const file = res.tempFiles[0]
        this.uploadFile(file)
      }
    })
  },

  // 从相册选图片
  chooseImage() {
    wx.chooseImage({
      count: 1,
      success: (res) => {
        const file = {
          path: res.tempFilePaths[0],
          name: '图片_' + new Date().getTime() + '.jpg'
        }
        this.uploadFile(file)
      }
    })
  },

  // 上传文件到服务器
  uploadFile(file) {
    wx.showLoading({ title: '上传中...' })
    
    wx.uploadFile({
      url: app.globalData.apiBaseUrl + '/api/upload',
      filePath: file.path,
      name: 'file',
      formData: {
        filename: file.name
      },
      success: (res) => {
        wx.hideLoading()
        try {
          const data = JSON.parse(res.data)
          console.log('Upload response:', data)
          if (data.success) {
            const category = data.data.category || '未分类'
            wx.showToast({ title: `上传成功！分类：${category}`, icon: 'success', duration: 2000 })
            this.loadRecentFiles()
          } else {
            wx.showToast({ title: data.message || '上传失败', icon: 'none' })
          }
        } catch (e) {
          console.error('Parse error:', e, res.data)
          wx.showToast({ title: '上传失败', icon: 'none' })
        }
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({ title: '上传失败，请检查网络', icon: 'none' })
      }
    })
  },

  // 获取最近文件列表
  loadRecentFiles() {
    wx.request({
      url: app.globalData.apiBaseUrl + '/api/files',
      success: (res) => {
        console.log('Files loaded:', res.data)
        if (res.data.success) {
          this.setData({
            recentFiles: res.data.data.slice(0, 5)
          })
          console.log('Recent files updated:', res.data.data.slice(0, 5))
        } else {
          console.error('Failed to load files:', res.data.message)
        }
      },
      fail: (err) => {
        console.error('Request failed:', err)
      }
    })
  },

  // 跳转到资料库
  goToLibrary() {
    wx.switchTab({ url: '/pages/library/library' })
  },

  // 跳转到对话页
  goToChat() {
    wx.switchTab({ url: '/pages/chat/chat' })
  },

  // 跳转到历史记录
  goToHistory() {
    wx.navigateTo({ url: '/pages/history/history' })
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.loadRecentFiles()
    wx.stopPullDownRefresh()
  }
})
