const app = getApp()

Page({
  data: {
    files: [],
    searchKeyword: '',
    allFiles: []
  },

  onLoad() {
    this.loadFiles()
  },

  onShow() {
    this.loadFiles()
  },

  // 加载文件列表
  loadFiles() {
    app.request({
      url: '/api/files',
      success: (res) => {
        if (res.data.success) {
          this.setData({
            files: res.data.data,
            allFiles: res.data.data
          })
        }
      },
      fail: () => {
        wx.showToast({ title: '加载失败', icon: 'none' })
      }
    })
  },

  // 搜索
  onSearch(e) {
    const keyword = e.detail.value.toLowerCase()
    this.setData({ searchKeyword: keyword })
    
    if (!keyword) {
      this.setData({ files: this.data.allFiles })
      return
    }
    
    const filtered = this.data.allFiles.filter(file => 
      file.name.toLowerCase().includes(keyword)
    )
    this.setData({ files: filtered })
  },

  // 查看文件详情
  viewFile(e) {
    const id = e.currentTarget.dataset.id
    const file = this.data.files.find(f => f.id === id)
    if (!file) return

    const categoryIcon = { '数学': '📐', '英语': '🔤', '政治': '📜', '计算机': '💻', '其他': '📂' }
    const icon = categoryIcon[file.category] || '📂'

    wx.showActionSheet({
      itemList: ['📋 查看详情', '🗑️ 删除文件'],
      success: (res) => {
        if (res.tapIndex === 0) {
          wx.showModal({
            title: `${icon} 文件详情`,
            content: `📄 文件名：${file.name}\n🗂️ 分类：${file.category}\n📁 格式：${file.type.toUpperCase()}\n📦 大小：${file.size}\n🕐 上传时间：${file.time}`,
            showCancel: false,
            confirmText: '知道了'
          })
        } else if (res.tapIndex === 1) {
          this.deleteFile(id)
        }
      }
    })
  },

  // 删除文件
  deleteFile(fileId) {
    wx.showModal({
      title: '确认删除',
      content: '确定要删除这个文件吗？删除后无法恢复。',
      confirmColor: '#ff4444',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '删除中...' })

          app.request({
            url: '/api/files/' + fileId,
            method: 'DELETE',
            success: (res) => {
              wx.hideLoading()
              if (res.data.success) {
                wx.showToast({ title: '删除成功', icon: 'success' })
                this.loadFiles()
              } else {
                wx.showToast({ title: res.data.message || '删除失败', icon: 'none' })
              }
            },
            fail: () => {
              wx.hideLoading()
              wx.showToast({ title: '删除失败', icon: 'none' })
            }
          })
        }
      }
    })
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.loadFiles()
    wx.stopPullDownRefresh()
  },

  // 跳转到上传页面
  goToUpload() {
    wx.switchTab({
      url: '/pages/index/index'
    })
  }
})
