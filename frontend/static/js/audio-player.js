// frontend/static/js/audio-player.js
/**
 * Audio Player Worklet
 */

export async function startAudioPlayerWorklet() {
    const audioContext = new AudioContext({
        sampleRate: 24000
    });
    
    // The path for pcm-player-processor.js is relative to audio-player.js
    const workletURL = new URL('./pcm-player-processor.js', import.meta.url);
    await audioContext.audioWorklet.addModule(workletURL);
    
    const audioPlayerNode = new AudioWorkletNode(audioContext, 'pcm-player-processor');

    audioPlayerNode.connect(audioContext.destination);

    return [audioPlayerNode, audioContext];
}
