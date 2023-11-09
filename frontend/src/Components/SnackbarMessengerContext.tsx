import {createContext, ReactElement, ReactNode, useContext, useEffect, useState} from "react";
import {AlertProps, Snackbar, SnackbarProps} from "@mui/material";
import {useImmer} from "use-immer";
import Alert from "@mui/material/Alert";

export type SnackbarMessage = {message: ReactNode} & Pick<AlertProps, "severity">

export interface ISnackbarMessengerContext {
    snackbarMessages: (SnackbarMessage & {key: number})[]
    postSnackbarMessage:  (message: SnackbarMessage) => void
    markRead: () => void
}

const SnackbarMessengerContext = createContext({} as ISnackbarMessengerContext)

export const useSnackbarMessenger = () => useContext(SnackbarMessengerContext)

export const SnackbarMessengerContextProvider = ({children}: {children: ReactElement}) => {
    const [messages, setMessages] =
        useImmer<ISnackbarMessengerContext["snackbarMessages"]>([])
    const postSnackbarMessage = (message: SnackbarMessage) => setMessages(messages => {
        messages.push({key: new Date().getTime(), ...message})
    })
    const markRead = () => setMessages(messages => {
        messages.shift()
    })

    return <SnackbarMessengerContext.Provider value={{postSnackbarMessage, snackbarMessages: messages, markRead}}>
        {children}
    </SnackbarMessengerContext.Provider>
}

export const SnackbarMessenger = (props: Omit<SnackbarProps, "message"|"action"|"key"|"open"|"onClose">) => {
    const {snackbarMessages, markRead} = useSnackbarMessenger()
    const [open, setOpen] = useState<boolean>(snackbarMessages.length > 0)
    const handleClose = (_: any, reason?: string) => {
        if (reason === 'clickaway') return
        markRead()
    }
    useEffect(() => setOpen(snackbarMessages.length > 0), [snackbarMessages])

    return <Snackbar
        key={snackbarMessages[0]?.key ?? 'snackbar-messenger'}
        open={open}
        onClose={handleClose}
        anchorOrigin={{vertical: 'bottom', horizontal: 'left'}}
        {...props}
    >
        <Alert
            onClose={handleClose}
            severity={snackbarMessages[0]?.severity || "info"}
        >
            {snackbarMessages[0]?.message}
        </Alert>
    </Snackbar>
}
