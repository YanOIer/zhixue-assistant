const app = getApp()

Page({
  data: {
    loading: true,
    ragStatus: '',
    ragStatusColor: '',
    apiStatus: '',
    apiStatusColor: '',
    classifierStatus: '',
    classifierStatusColor: '',
    runMode: '',
    runModeDesc: '',
    docCount: 0,
    chunkCount: 0
  },

  onLoad() {
    this.loadInfo()
  },

  loadInfo() {
    app.request({
      url: '/api/ai/info',
      success: (res) => {
        if (!res.data.success) return
        const d = res.data.data
        const ragReady = d.rag_system.status === 'ready'
        const clsReady = d.document_classifier.status === 'ready'
        const stats = d.rag_system.stats || {}
        const apiConfigured = d.ai_model.configured
        const kimiKey = apiConfigured && d.ai_model.description && !d.ai_model.description.includes('未配置')

        this.setData({
          loading: false,
          ragStatus: ragReady ? '✅ RAG智能模式' : '⚙️ 本地检索模式',
          ragStatusColor: ragReady ? '#28a745' : '#e67e22',
          apiStatus: apiConfigured && kimiKey ? '✅ KIMI已配置' : '⚠️ 使用本地检索',
          apiStatusColor: apiConfigured && kimiKey ? '#28a745' : '#e67e22',
          classifierStatus: clsReady ? '✅ 已就绪' : '⏳ 未加载',
          classifierStatusColor: clsReady ? '#28a745' : '#999',
          runMode: ragReady && kimiKey ? 'RAG 检索增强生成' : '本地关键词检索',
          runModeDesc: ragReady && kimiKey
            ? '查询时先向量化问题 → FAISS检索相关片段 → 送入KIMI大模型生成回答'
            : '查询时对知识库文本做关键词匹配，提取相关段落直接返回（无需大模型）',
          docCount: stats.document_count || 0,
          chunkCount: stats.chunk_count || 0
        })
      },
      fail: () => {
        this.setData({ loading: false })
      }
    })
  }
})
