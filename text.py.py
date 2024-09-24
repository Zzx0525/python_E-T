import streamlit as st
import pandas as pd
import random
import time

def main():
    st.title("英文測驗")
    st.markdown('### by.ZX')

    # 初始化一些会话状态变量
    if 'counter' not in st.session_state:
        st.session_state.counter = 0

    if 'error_words' not in st.session_state:
        st.session_state.error_words = {}

    if 'score' not in st.session_state:
        st.session_state.score = 0

    if 'quiz_active' not in st.session_state:
        st.session_state.quiz_active = True

    # 将上传文件的部分移到侧边栏
    uploaded_file = st.sidebar.file_uploader("檔案上傳(.xlsx)", type=["xlsx"])
    
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)

        # 初始化问题索引
        if 'question_index' not in st.session_state:
            st.session_state.question_index = list(range(len(df)))
            random.shuffle(st.session_state.question_index)

        # 无限出题循环
        if st.session_state.quiz_active:
            generate_question(df)

        # 结束按钮
        if st.button("结束"):
            st.session_state.quiz_active = False
            total_questions = st.session_state.counter
            correct_answers = st.session_state.score
            accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

            st.write(f"你总共回答了 {total_questions} 道题目，正确率为 {accuracy:.2f}%")
            
            # 输出错误单词表格
            if st.session_state.error_words:
                error_df = pd.DataFrame(list(st.session_state.error_words.items()), columns=['单词', '错误次数'])
                st.write("以下是你答错的单词：")
                st.table(error_df)

            # 重置按钮
            if st.button("重新开始"):
                reset_quiz()  # 调用重置函数

def generate_question(df):
    # 如果超出题目数量，重新打乱问题
    if st.session_state.counter >= len(df):
        st.session_state.counter = 0
        random.shuffle(st.session_state.question_index)

    # 获取当前的问题索引
    current_question_index = st.session_state.question_index[st.session_state.counter]

    # 检查是否已经保存了当前题目的选项（防止每次都随机）
    if f'question_{st.session_state.counter}' not in st.session_state:
        correct_row = df.iloc[current_question_index]
        correct_answer = correct_row['English']
        question = correct_row['Chinese']

        wrong_answers = df[df['English'] != correct_answer].sample(n=3)['English'].tolist()
        options = wrong_answers + [correct_answer]
        random.shuffle(options)

        # 保存当前问题和选项到 session_state
        st.session_state[f'question_{st.session_state.counter}'] = question
        st.session_state[f'options_{st.session_state.counter}'] = options
        st.session_state[f'correct_answer_{st.session_state.counter}'] = correct_answer
    else:
        # 从 session_state 中获取已保存的问题和选项
        question = st.session_state[f'question_{st.session_state.counter}']
        options = st.session_state[f'options_{st.session_state.counter}']
        correct_answer = st.session_state[f'correct_answer_{st.session_state.counter}']

    st.header(f"問題{st.session_state.counter + 1}: {question}")
    user_choice = st.radio("請選擇一個選項:", options, key=f"radio_{st.session_state.counter}")

    # 如果用户点击提交按钮
    if st.button("提交", key=f"submit_{st.session_state.counter}"):
        if user_choice == correct_answer:
            st.success("答對了！!")
            st.session_state.score += 1
        else:
            st.error(f"答錯了! 正确答案是 {correct_answer}。")
            if correct_answer not in st.session_state.error_words:
                st.session_state.error_words[correct_answer] = 1
            else:
                st.session_state.error_words[correct_answer] += 1

        # 更新计数器，自动进入下一题
        st.session_state.counter += 1

        # 页面会自动刷新，因为 st.session_state 更新了
        # 不需要手动调用 experimental_rerun()

def reset_quiz():
    """重置测验状态"""
    st.session_state.counter = 0
    st.session_state.score = 0
    st.session_state.error_words = {}
    st.session_state.quiz_active = True
    st.session_state.question_index = []  # 清除问题索引
    st.write("测验已重新开始，请上传文件以开始新的测验。")  # 提示用户

if __name__ == '__main__':
    main()


