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
    wx.request({
      url: app.globalData.apiBaseUrl + '/api/chat',
      method: 'POST',
      header: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      data: { question: content },
      success: (res) => {
        if (res.data.success) {
          const aiMsg = {
            id: Date.now() + 1,
            type: 'ai',
            content: res.data.answer,
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
  }
})
