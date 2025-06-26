import streamlit as st
from audiorecorder import audiorecorder
from openai_service import stt, ask_gpt, tts




def main():
    st.set_page_config(
        page_title='😎Voice Chatbot😎',
        page_icon="🎤",
        layout='wide'
    )
    st.header('🎤Voice Chatbot🎤')
    st.markdown('---')

    with st.expander('Voice Chatbot 프로그램 처리절차', expanded=False):
        st.write(
            """
            1. 녹음하기 버튼을 눌러 질문을 녹음합니다.
            2. 녹음이 완료되면 자동으로 Whisper모델을 이용해 음성을 텍스트로 변환합니다. 
            3. 변환된 텍스트로 LLM에 질의후 응답을 받습니다.
            4. LLM의 응답을 다시 TTS모델을 사용해 음성으로 변환하고 이를 사용자에게 들려줍니다.
            5. 모든 질문/답변은 채팅형식의 텍스트로 제공합니다.
            """
        )

    # session_state 초기화
    if 'messages' not in st.session_state:
        st.session_state['messages'] = [
            {'role': 'system', 'content': '당신은 친절한 챗봇입니다.'}
        ]
    if 'check_reset' not in st.session_state:
        st.session_state['check_reset'] = False

    with st.sidebar:
        model = st.radio(label='GPT 모델', options=['gpt-4.1', 'gpt-4o', 'gpt-4o-mini'], index=2)
        print(f'model={model}')

        if st.button(label='초기화'):
            st.session_state['check_reset'] = True
            st.session_state['messages'] = [
                {'role': 'system', 'content': '당신은 친절한 챗봇입니다.'}
            ]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader('녹음하기')

        audio = audiorecorder()

        if (audio.duration_seconds > 0) and (not st.session_state['check_reset']):
            # 음원 재생
            st.audio(audio.export().read())

            # stt 사용자 프롬프트 추출
            prompt = stt(audio)
            print(f'prompt={prompt}')

            # chat completion 호출
            # - messages에 추가
            st.session_state['messages'].append({'role': 'user', 'content': prompt})
            # - llm 요청
            response = ask_gpt(st.session_state['messages'], model)
            st.session_state['messages'].append({'role': 'assistant', 'content': response})
            print(f'response={response}')

            # llm 응답을 tts모델을 통해 음원파일로 변환/재생
            base64_encoded = tts(response)
            # print(base64_encoded)
            st.html(f'''
            <audio autoplay='true'>
                <source src='data:audio/mp3;base64,{base64_encoded}' type='audio/mp3'/>
            </audio>
            ''')

    with col2:
        st.subheader('질문/답변')

        if (audio.duration_seconds > 0) and (not st.session_state['check_reset']):
            for message in st.session_state['messages']:
                role = message['role']  # system/user/assistant
                content = message['content']

                if role == 'system':
                    continue

                with st.chat_message(role):
                    st.markdown(content)
        else:
            st.session_state['check_reset'] = False  # 초기화상태 값은 원복


if __name__ == '__main__':
    main()