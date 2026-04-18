const app = getApp()

Page({
  data: {
    aiInfo: null,
    apiBaseUrl: ''
  },

  onLoad() {
    this.setData({
      apiBaseUrl: app.globalData.apiBaseUrl
    })
    this.loadAIInfo()
  },

  // 加载AI系统信息
  loadAIInfo() {
    app.request({
      url: '/api/ai/info',
      success: (res) => {
        if (res.data.success) {
          this.setData({ aiInfo: res.data.data })
        }
      }
    })
  },

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

  // 清空历史记录
  clearHistory() {
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

  configureApi() {
    wx.showModal({
      title: '设置后端地址',
      editable: true,
      placeholderText: '例如：http://127.0.0.1:8000',
      content: this.data.apiBaseUrl,
      success: (res) => {
        if (res.confirm && res.content) {
          app.setApiBaseUrl(res.content)
          this.setData({ apiBaseUrl: app.globalData.apiBaseUrl })
          wx.showToast({ title: '保存成功', icon: 'success' })
          this.loadAIInfo()
        }
      }
    })
  },

  // 关于我们
  about() {
    wx.showModal({
      title: '关于智学助手',
      content: '智学助手是一款基于RAG（检索增强生成）技术的智能学习助手。\n\n功能特点：\n• 上传学习资料（PDF/Word/TXT）\n• 基于资料的智能问答\n• 显示答案来源，可追溯验证\n\n版本：1.0.0\n开发者：人工智能课程小组',
      showCancel: false
    })
  },

  // 查看AI系统信息
  viewAIInfo() {
    if (!this.data.aiInfo) {
      wx.showToast({ title: '信息加载中', icon: 'loading' })
      return
    }

    const info = this.data.aiInfo
    const ragStatus = info.rag_system.status === 'ready' ? '✅ 已就绪' : '🧪 演示模式'
    const classifierStatus = info.document_classifier.status === 'ready' ? '✅ 已就绪' : '⏳ 未初始化'

    const content = `RAG系统: ${ragStatus}
文档分类器: ${classifierStatus}

技术详情:
• Embedding: ${info.rag_system.components.embedding}
• 检索: ${info.rag_system.components.retrieval}
• 重排序: ${info.rag_system.components.reranker}
• LLM: ${info.rag_system.components.llm}

文档分类:
• 算法: ${info.document_classifier.algorithm}
• 类别: ${info.document_classifier.categories.join(', ')}`

    wx.showModal({
      title: 'AI系统信息',
      content: content,
      showCancel: false
    })
  }
})
