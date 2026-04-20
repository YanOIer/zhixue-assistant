const app = getApp()

Page({
  data: {
    loading: true,
    ragStatus: '',
    ragStatusColor: '',
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

        this.setData({
          loading: false,
          ragStatus: ragReady ? '✅ 向量检索模式（RAG）' : '⚙️ 本地关键词检索模式',
          ragStatusColor: ragReady ? '#28a745' : '#e67e22',
          classifierStatus: clsReady ? '✅ 已就绪' : '⏳ 未加载',
          classifierStatusColor: clsReady ? '#28a745' : '#999',
          runMode: ragReady ? 'RAG 检索增强生成' : '本地关键词检索降级',
          runModeDesc: ragReady
            ? '查询时先向量化问题 → FAISS检索相关片段 → 重排序 → 送入大模型生成回答'
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
