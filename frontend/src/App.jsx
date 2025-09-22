import { useEffect, useState } from 'react'

function App() {
  const [message, setMessage] = useState('Cargando...')

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const baseUrl =
          import.meta.env.VITE_API_BASE_URL ??
          (import.meta.env.DEV ? 'http://localhost:5000/api' : '/api')
        const endpoint = baseUrl.endsWith('/')
          ? `${baseUrl}status`
          : `${baseUrl}/status`

        const response = await fetch(endpoint)

        if (!response.ok) {
          throw new Error(`Respuesta inesperada: ${response.status}`)
        }

        const data = await response.json()

        if (data && typeof data.message === 'string') {
          setMessage(data.message)
        } else {
          setMessage('Respuesta del backend inválida')
        }
      } catch (error) {
        console.error('Error al obtener el estado del backend:', error)
        setMessage('Error al conectar con el backend')
      }
    }

    fetchStatus()
  }, [])

  return (
    <div className="p-10 text-xl">
      <h1>{message}</h1>
    </div>
  )
}

export default App
