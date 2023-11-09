import {createContext, PropsWithChildren} from "react";
import {useImmer} from "use-immer";

type UndoRedoState = {
    history: any[]
    current_index: number
}

interface IUndoRedo {
    current: any
    can_undo: boolean
    can_redo: boolean
    undo: () => void
    redo: () => void
    set: (payload: any) => void
    reset: () => void
    update: (payload: any) => void
}

export const UndoRedoContext = createContext({} as IUndoRedo)

export default function UndoRedoProvider({children}: PropsWithChildren<any>) {
    const [state, setState] = useImmer<UndoRedoState>({
        history: [],
        current_index: 0
    })

    return <UndoRedoContext.Provider value={{
        current: state.history[state.current_index],
        can_undo: state.current_index > 0,
        can_redo: state.current_index < state.history.length - 1,
        undo: () => setState({
            ...state,
            current_index: state.current_index - 1 >= 0 ? state.current_index - 1 : 0
        }),
        redo: () => setState({
            ...state,
            current_index: state.current_index + 1
        }),
        set: (payload: any) => setState({
            history: [payload],
            current_index: 0
        }),
        reset: () => setState({
            history: [state.history.length? state.history[0] : []],
            current_index: 0
        }),
        update: (payload: any) => setState({
            history: [...state.history.slice(0, state.current_index + 1), payload],
            current_index: state.current_index + 1
        })
    }}>
        {children}
    </UndoRedoContext.Provider>
}