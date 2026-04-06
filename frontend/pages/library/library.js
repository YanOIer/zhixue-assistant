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
    wx.request({
      url: app.globalData.apiBaseUrl + '/api/files',
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
    wx.showToast({ title: '查看文件: ' + id, icon: 'none' })
    // 后续可以添加文件详情页
  }
})
