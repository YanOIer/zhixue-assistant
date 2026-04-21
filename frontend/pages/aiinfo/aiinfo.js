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

        this.setData({
          loading: false,
          ragStatus: ragReady ? '✅ 向量检索就绪' : '⚙️ 等待初始化',
          ragStatusColor: ragReady ? '#28a745' : '#e67e22',
          classifierStatus: clsReady ? '✅ 已就绪' : '⏳ 未加载',
          classifierStatusColor: clsReady ? '#28a745' : '#999',
          runMode: '本地语义检索',
          runModeDesc: '问题向量化 → FAISS检索 → 返回相关片段',
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
