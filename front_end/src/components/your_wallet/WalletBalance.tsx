
import { Token } from "../Main"
import {useEthers, useTokenBalance} from '@usedapp/core'
import {formatUnits} from "@ethersproject/units"
import {BalanceMsg} from "../../components/BalanceMsg"

export interface WalletbalanceProps {
    token: Token
}

export const WalletBalance = ({token}: WalletbalanceProps) => {
    const {image, address, name} = token
    const {account} = useEthers()
    const tokenBalance = useTokenBalance(address, account)
    const formattedTokenBlanace: number = tokenBalance ? parseFloat(formatUnits(tokenBalance, 18)) : 0
    return (<BalanceMsg label={`Your Un-Staked ${name} balance`} tokenImgSrc={image} amount={formattedTokenBlanace}/>)
} 


