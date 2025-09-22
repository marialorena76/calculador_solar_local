import { useEffect, useState } from 'react'

function App() {
  const [message, setMessage] = useState('Cargando...')

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/status')

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
