const app = getApp()

Page({
  data: {
    history: [],
    isLoading: false
  },

  onLoad() {
    this.loadHistory()
  },

  onShow() {
    this.loadHistory()
  },

  // 加载对话历史
  loadHistory() {
    this.setData({ isLoading: true })

    app.request({
      url: '/api/chat/history',
      success: (res) => {
        if (res.data.success) {
          const history = (res.data.data || []).map(item => ({
            ...item,
            time: (item.time || '').substring(0, 16)
          }))
          this.setData({
            history,
            isLoading: false
          })
        } else {
          this.setData({ isLoading: false })
          wx.showToast({ title: '加载失败', icon: 'none' })
        }
      },
      fail: () => {
        this.setData({ isLoading: false })
        wx.showToast({ title: '网络错误', icon: 'none' })
      }
    })
  },

  // 查看对话详情
  viewDetail(e) {
    const item = e.currentTarget.dataset.item
    wx.showModal({
      title: '对话详情',
      content: `问题：${item.question}\n\n回答：${item.answer.substring(0, 200)}${item.answer.length > 200 ? '...' : ''}`,
      showCancel: false
    })
  },

  // 继续对话
  continueChat(e) {
    const question = e.currentTarget.dataset.question
    wx.switchTab({
      url: '/pages/chat/chat'
    })
    // 将问题存储到全局，在chat页面读取
    app.globalData.pendingQuestion = question
  },

  // 清空历史
  clearAllHistory() {
    wx.showModal({
      title: '确认清空',
      content: '确定要清空所有对话历史吗？此操作不可恢复。',
      confirmColor: '#ff4444',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '清空中...' })

          app.request({
            url: '/api/chat/history',
            method: 'DELETE',
            success: (res) => {
              wx.hideLoading()
              if (res.data.success) {
                wx.showToast({ title: '清空成功', icon: 'success' })
                this.setData({ history: [] })
              } else {
                wx.showToast({ title: res.data.message || '清空失败', icon: 'none' })
              }
            },
            fail: () => {
              wx.hideLoading()
              wx.showToast({ title: '清空失败', icon: 'none' })
            }
          })
        }
      }
    })
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.loadHistory()
    wx.stopPullDownRefresh()
  }
})
