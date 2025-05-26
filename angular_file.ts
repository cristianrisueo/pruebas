// voicebot.component.ts
import { Component, OnInit, OnDestroy } from '@angular/core';

@Component({
  selector: 'app-voicebot',
  templateUrl: './voicebot.component.html',
  styleUrls: ['./voicebot.component.css']
})
export class VoicebotComponent implements OnInit, OnDestroy {
  ws: WebSocket | null = null;
  mediaRecorder: MediaRecorder | null = null;
  audioChunks: Blob[] = [];
  isRecording = false;

  ngOnInit() {
    this.connectWebSocket();
  }

  ngOnDestroy() {
    if (this.ws) this.ws.close();
  }

  connectWebSocket() {
    this.ws = new WebSocket(`ws://${window.location.host}/ws`);

    this.ws.onopen = () => {
      console.log('✅ WebSocket conectado');
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('📩 Mensaje recibido', data);
      } catch (e) {
        console.log('❌ Mensaje no JSON', event.data);
      }
    };

    this.ws.onclose = () => {
      console.log('🔌 WebSocket cerrado');
      this.ws = null;
    };

    this.ws.onerror = (error) => {
      console.error('⚠️ WebSocket error', error);
    };
  }

  async sendAudio() {
    if (!this.isRecording) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this.mediaRecorder = new MediaRecorder(stream, {
          mimeType: 'audio/webm',
          audioBitsPerSecond: 128000
        });

        this.mediaRecorder.ondataavailable = (event) => {
          this.audioChunks.push(event.data);
        };

        this.mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
          const arrayBuffer = await audioBlob.arrayBuffer();

          if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(arrayBuffer);
            console.log(`📤 Audio enviado (${arrayBuffer.byteLength} bytes)`);
          } else {
            console.error('🚫 WebSocket no conectado');
          }

          this.audioChunks = [];
        };

        this.mediaRecorder.start();
        this.isRecording = true;
        console.log('🎙️ Grabación iniciada');
      } catch (err: any) {
        console.error('❌ Error al iniciar grabación:', err.message);
      }
    } else {
      this.mediaRecorder?.stop();
      this.isRecording = false;
      console.log('🛑 Grabación detenida');
    }
  }
}
