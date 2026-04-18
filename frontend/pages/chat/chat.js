const app = getApp()

Page({
  data: {
    messages: [
      {
        id: 1,
        type: 'ai',
        content: '你好！我是智学助手。请上传学习资料后，我可以基于资料内容为你解答问题。',
        sources: []
      }
    ],
    inputValue: '',
    isLoading: false,
    scrollToView: ''
  },

  onLoad() {
    this.consumePendingQuestion()
  },

  onShow() {
    this.consumePendingQuestion()
  },

  consumePendingQuestion() {
    if (app.globalData.pendingQuestion) {
      this.setData({ inputValue: app.globalData.pendingQuestion })
      app.globalData.pendingQuestion = null
    }
  },

  onInput(e) {
    this.setData({ inputValue: e.detail.value })
  },

  // 发送消息
  sendMessage() {
    const content = this.data.inputValue.trim()
    if (!content || this.data.isLoading) return

    // 添加用户消息
    const userMsg = {
      id: Date.now(),
      type: 'user',
      content: content,
      sources: []
    }
    
    this.setData({
      messages: [...this.data.messages, userMsg],
      inputValue: '',
      isLoading: true,
      scrollToView: 'msg-' + userMsg.id
    })

    // 调用后端API
    app.request({
      url: '/api/chat',
      method: 'POST',
      header: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      data: { question: content },
      success: (res) => {
        if (res.data.success) {
          const suffix = res.data.mode === 'rag' ? '\n\n[回答模式] RAG 检索增强' : '\n\n[回答模式] 本地知识库检索'
          const aiMsg = {
            id: Date.now() + 1,
            type: 'ai',
            content: res.data.answer + suffix,
            sources: res.data.sources || []
          }
          this.setData({
            messages: [...this.data.messages, aiMsg],
            isLoading: false,
            scrollToView: 'msg-' + aiMsg.id
          })
        } else {
          this.handleError(res.data.message || '获取回答失败')
        }
      },
      fail: () => {
        this.handleError('网络错误，请稍后重试')
      }
    })
  },

  handleError(message) {
    const errorMsg = {
      id: Date.now() + 1,
      type: 'ai',
      content: '抱歉，' + message,
      sources: []
    }
    this.setData({
      messages: [...this.data.messages, errorMsg],
      isLoading: false,
      scrollToView: 'msg-' + errorMsg.id
    })
  },

  // 长按复制消息
  onMessageLongPress(e) {
    const content = e.currentTarget.dataset.content
    wx.setClipboardData({
      data: content,
      success: () => {
        wx.showToast({ title: '已复制', icon: 'success' })
      }
    })
  },

  // 清空对话
  clearChat() {
    wx.showModal({
      title: '确认清空',
      content: '确定要清空当前对话吗？',
      success: (res) => {
        if (res.confirm) {
          this.setData({
            messages: [
              {
                id: 1,
                type: 'ai',
                content: '你好！我是智学助手。请上传学习资料后，我可以基于资料内容为你解答问题。',
                sources: []
              }
            ]
          })
        }
      }
    })
  }
})
