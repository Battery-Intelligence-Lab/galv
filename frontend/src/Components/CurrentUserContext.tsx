import {createContext, useContext, useState} from "react";
import {KnoxUser, LoginApi, User} from "../api_codegen";
import {useMutation, useQueryClient} from "@tanstack/react-query";
import {AxiosError, AxiosResponse} from "axios";
import axios from "axios/index";
import {useSnackbarMessenger} from "./SnackbarMessengerContext";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";

export type LoginUser = Pick<KnoxUser, "token"> & User

export interface ICurrentUserContext {
    user: LoginUser|null
    login: (username: string, password: string) => void
    logout: () => void
    loginFormOpen: boolean
    setLoginFormOpen: (open: boolean) => void
}

export const CurrentUserContext = createContext({} as ICurrentUserContext)

export const useCurrentUser = () => useContext(CurrentUserContext)

export default function CurrentUserContextProvider({children}: {children: React.ReactNode}) {
    const local_user_string = window.localStorage.getItem('user')
    const local_user: LoginUser|null = JSON.parse(local_user_string || 'null')
    if (local_user && local_user.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${local_user.token}`
    }

    const [user, setUser] = useState<LoginUser|null>(local_user ?? null)
    const [username, setUsername] = useState<string>('')
    const [password, setPassword] = useState<string>('')
    const [loginFormOpen, setLoginFormOpen] = useState<boolean>(false)

    const {postSnackbarMessage} = useSnackbarMessenger()

    const queryClient = useQueryClient()
    const api_handler = new LoginApi()
    const Login = useMutation<AxiosResponse<KnoxUser>, AxiosError>({
        mutationFn: () => {
            console.log('login', username, password)
            return api_handler.loginCreate({
                headers: {Authorization: `Basic ${btoa(username + ":" + password)}`}
            })
        },
        onSuccess: (data: AxiosResponse<KnoxUser>) => {
            axios.defaults.headers.common['Authorization'] = `Bearer ${data.data.token}`
            window.localStorage.setItem('user', JSON.stringify(data.data))
            setUser(data.data as unknown as LoginUser)
            queryClient.invalidateQueries({predicate: (q: any) => true})
        }
    })

    const Logout = () => {
        if (user) {
            window.localStorage.removeItem('user')
            setUser(null)
            axios.defaults.headers.common['Authorization'] = undefined
            queryClient.invalidateQueries({predicate: (q: any) => true})
        }
    }

    const do_login = (username: string, password: string) => {
        setUsername(username)
        setPassword(password)
        Login.mutate()
    }

    axios.interceptors.response.use(
        null,
        // 401 should log the user out and display a message
        (error) => {
            if (error.response?.status === 401) {
                Logout()
                postSnackbarMessage({
                    message: <Stack direction="row" spacing={1}>
                        You have been logged out.
                        <Button onClick={() => setLoginFormOpen(true)}>Log in</Button>
                    </Stack>,
                    severity: 'warning'
                })
                return Promise.reject(error)
            }
        }
    )

    return <CurrentUserContext.Provider value={{user, login: do_login, logout: Logout, loginFormOpen, setLoginFormOpen}}>
        {children}
    </CurrentUserContext.Provider>
}
