const app = getApp()

Page({
  data: {
    files: [],
    searchKeyword: '',
    currentCategory: '全部',
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

  // 刷新文件列表
  refreshFiles() {
    wx.showLoading({ title: '刷新中...' })
    this.loadFiles()
    setTimeout(() => {
      wx.hideLoading()
      wx.showToast({ title: '已刷新', icon: 'success' })
    }, 500)
  },

  // 搜索
  onSearch(e) {
    const keyword = e.detail.value
    this.setData({ searchKeyword: keyword })
    this.filterFiles()
  },

  // 清除搜索
  clearSearch() {
    this.setData({ searchKeyword: '' })
    this.filterFiles()
  },

  // 按分类筛选
  filterByCategory(e) {
    const category = e.currentTarget.dataset.category
    this.setData({ currentCategory: category })
    this.filterFiles()
  },

  // 综合筛选文件
  filterFiles() {
    const { allFiles, searchKeyword, currentCategory } = this.data
    
    let filtered = allFiles
    
    // 分类筛选
    if (currentCategory !== '全部') {
      filtered = filtered.filter(file => file.category === currentCategory)
    }
    
    // 搜索筛选
    if (searchKeyword) {
      const keyword = searchKeyword.toLowerCase()
      filtered = filtered.filter(file => 
        file.name.toLowerCase().includes(keyword) ||
        file.category.toLowerCase().includes(keyword)
      )
    }
    
    this.setData({ files: filtered })
  },

  // 查看文件详情
  viewFile(e) {
    const id = e.currentTarget.dataset.id
    const file = this.data.files.find(f => f.id === id)
    if (!file) return

    const categoryIcon = { '数学': '📐', '英语': '🔤', '政治': '📜', '计算机': '💻', '其他': '📂' }
    const icon = categoryIcon[file.category] || '📂'
    const typeIcon = {
      'pdf': '📄', 'txt': '📝', 'docx': '📝', 'md': '📝',
      'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'bmp': '🖼️', 'gif': '🖼️'
    }
    const fileIcon = typeIcon[file.type] || '📎'

    wx.showModal({
      title: `${icon} ${file.category}`,
      content: `${fileIcon} 文件名：${file.name}\n🗂️ 分类：${file.category}\n📁 格式：${file.type.toUpperCase()}\n📦 大小：${file.size}\n🕐 上传时间：${file.time}`,
      showCancel: true,
      confirmText: '删除',
      cancelText: '关闭',
      confirmColor: '#ff4444',
      success: (res) => {
        if (res.confirm) {
          this.deleteFile(id)
        }
      }
    })
  },

  // 删除文件
  deleteFile(fileId) {
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
