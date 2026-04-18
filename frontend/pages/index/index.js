const app = getApp()

Page({
  data: {
    recentFiles: [],
    backendReady: false,
    backendMode: '检查中'
  },

  onLoad() {
    this.checkBackend()
    this.loadRecentFiles()
  },

  onShow() {
    this.checkBackend()
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
      extension: ['pdf', 'txt', 'docx', 'md'],
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
      success: (res) => {
        wx.hideLoading()
        try {
          const data = JSON.parse(res.data)
          console.log('Upload response:', data)
          if (data.success) {
            const category = data.data.category || '未分类'
            const confidence = data.data.classification ?
              Math.round(data.data.classification.confidence * 100) : 0
            const modeText = data.data.ragIndexed ? '已加入 RAG 检索' : '已加入本地知识库'

            // 显示详细的分类结果
            wx.showModal({
              title: '上传成功',
              content: `文件名：${data.data.filename}\n分类：${category}\n置信度：${confidence}%\n状态：${modeText}`,
              showCancel: false,
              success: () => {
                this.loadRecentFiles()
              }
            })
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
        wx.showToast({ title: '上传失败，请检查后端地址', icon: 'none' })
      }
    })
  },

  checkBackend() {
    app.request({
      url: '/',
      success: (res) => {
        const ok = !!(res.data && res.data.message)
        this.setData({
          backendReady: ok,
          backendMode: ok
            ? (res.data.rag_ready ? 'RAG 模式已就绪' : '本地检索演示模式')
            : '连接失败'
        })
      },
      fail: () => {
        this.setData({
          backendReady: false,
          backendMode: '后端未连接'
        })
      }
    })
  },

  // 获取最近文件列表
  loadRecentFiles() {
    app.request({
      url: '/api/files',
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
    this.checkBackend()
    this.loadRecentFiles()
    wx.stopPullDownRefresh()
  }
})
