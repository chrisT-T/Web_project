<template>
    <div class="all">
        <header>
            <div class="logo">
                <img src="../assets/img/Code_logo.png" alt="Code_logo" id="code_logo">
                <h2>CODING</h2>
            </div>
        </header>
        <main class="main">
            <div class="bg_img">
                <div id="photo">
                    <img src="../assets/img/1.png" />
                    <img src="../assets/img/2.png" />
                    <img src="../assets/img/3.png" />
                    <img src="../assets/img/1.png" />
                </div>
            </div>
            <div class="inbox">
              <div class="login_box">
                  <button class="log_header">
                      <span>LOGIN</span>
                  </button>
                  <div class="context" id="c_1">
                      <input type="text" placeholder="Username" id="username" v-model="data.username">
                      <input type="password" placeholder="Password" id="password" v-model="data.password">
                      <button class="button" style="vertical-align:middle" id="btn_2" @click="SignupCheck"><span>Signup and Login</span></button>
                      <button class="button" style="vertical-align:middle" @click="loginCheck"><span>Login</span></button>
                  </div>
              </div>
            </div>
        </main>
    </div>
</template>

<script lang="ts" setup>
import router from '@/router'
import { onMounted, reactive } from 'vue'
import axios from 'axios'
import { ElNotification } from 'element-plus'

const data = reactive({
  username: '',
  password: '',
  flag: false,
  message: ''
})

const loginCheck = async () => {
  if (data.username.trim() === '' || data.password.trim() === '') {
    alert('Username or Password is missing')
  } else {
    await axios.get('http://127.0.0.1:5000/login', { params: { userName: data.username, userPassword: data.password } })
      .then(res => {
        data.flag = res.data.flag
        data.message = res.data.message
      }).catch(function (error) {
        console.log(error.response)
      })
    if (data.flag === false) {
      alert(data.message)
      return
    }
    router.replace({ name: 'projectmanage', params: { username: data.username } })
  }
}

const SignupCheck = async () => {
  if (data.username.trim() === '' || data.password.trim() === '') {
    alert('Username or Password is missing')
  } else {
    await axios.get('http://127.0.0.1:5000/signup', { params: { userName: data.username, userPassword: data.password } })
      .then(res => {
        data.flag = res.data.flag
        data.message = res.data.message
      }).catch(function (error) {
        console.log(error.response)
      })
    if (data.flag === false) {
      alert(data.message)
      return
    }
    router.replace({ name: 'projectmanage', params: { username: data.username } })
  }
}
// onMounted(() => {
//   ElNotification({
//     title: '使用指南',
//     message: 'This is the login page, the left side is the overview of the site, the right side is the login bar, unregistered users please click to register and log in',
//     type: 'info',
//     duration: 0
//   })
// })
</script>

<style scoped>
body {
    background-color: #fffbf7;
    min-width: 640px;
    min-height: 480px;
    background-attachment: fixed;
    /* 右上角渐变色 */
    /* background-image: linear-gradient(155deg, #ffdfb448, #fff9ca25); */
}

.all {
    display: flex;
    flex-direction: column;
    height: 100%;
}

header{
    display: flex;
    /* background: #fffbf7; */
    /* box-shadow: rgb(0 0 0 / 10%) 0px 2px 4px 0px; */
    box-sizing: border-box;
}

.logo {
    display: flex;
    align-items: center;
    font-family: 'Courier New', Courier, monospace;
    font-weight: lighter;
}

#code_logo {
  height: 70px;
  margin: auto 10px;
}

.main {
  display: flex;
  justify-content: center;
  align-items: center;
  /* flex-direction: column; */
  flex-grow: 1;
}

.bg_img {
width: 550px;
height: 400px;
/* border: dotted;
border-color:rgb(182, 141, 87); */
margin: 30px;
border-radius: 20px;
overflow: hidden;
box-shadow: rgb(0 0 0 / 27%) 1px 6px 20px;
}

#photo {
background-color: transparent;
width: 2200px;
animation: switch 20s ease-out infinite;
}

#photo > img {
float: left;
width: 550px;
height: 400px;
}

@keyframes switch {
0%, 25% {
    margin-left: 0;
}
30%, 55% {
    margin-left: -550px;
}
60%, 95% {
    margin-left: -1100px;
}
100% {
    margin-left: -1650px;
}
}

.inbox {
    width: 330px;
    height: 400px;
    margin: 30px;
    border-radius: 20px;
    background-color: #fff;
    overflow: hidden;
    box-shadow: rgb(0 0 0 / 27%) 1px 6px 20px;
    display: flex;
    flex-direction: column;
}

.login_box {
  height: 400px;
}

.log_header {
    height: 45px;
    width: 100%;
    background: var(--el-color-primary-dark-2);
    text-align: center;
    color: #fff;
    border: transparent;
    font-size: 25px;
}

.context {
  padding: 30px 15px;
  font-size: 40px;
  box-sizing: border-box;
  text-align: center;
  margin: 20px  20px;
  color: #114e80;
  height: 355px;
}

.context input {
    height: 30px;
    width: 100%;
    margin-bottom: 20px;
}

.button {
    display: inline-block;
    border-radius: 4px;
    background-color: var(--el-color-primary-light-3);
    border: none;
    color: #FFFFFF;
    text-align: center;
    font-size: 15px;
    padding: 10px;
    width: 100px;
    transition: all 0.3s;
    cursor: pointer;
    margin: 5px;
  }
  .button span {
    cursor: pointer;
    display: inline-block;
    position: relative;
    transition: 0.3s;
  }

#btn_2 {
  width: 200px;
}
  .button span:after {
    content: '\00bb';
    position: absolute;
    opacity: 0;
    top: 0;
    right: -10px;
    transition: 0.3s;
  }
  .button:hover span {
    padding-right: 25px;
  }
  .button:hover span:after {
    opacity: 1;
    right: 0;
  }
  .button:active {
    opacity: 0.7;
    transition: 0s;
  }

  input {
    border-radius: 10px;
    border-width: 1px;
    border-color: var(--el-color-primary-light-7) ;
  }
</style>
