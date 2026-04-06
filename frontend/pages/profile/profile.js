Page({
  data: {},

  // 清除缓存
  clearCache() {
    wx.showModal({
      title: '提示',
      content: '确定要清除缓存吗？',
      success: (res) => {
        if (res.confirm) {
          wx.clearStorage()
          wx.showToast({ title: '清除成功', icon: 'success' })
        }
      }
    })
  },

  // 关于我们
  about() {
    wx.showModal({
      title: '关于智学助手',
      content: '智学助手是一款基于RAG技术的智能学习资料管理工具。\n\n版本：1.0.0\n开发者：人工智能课程小组',
      showCancel: false
    })
  }
})
