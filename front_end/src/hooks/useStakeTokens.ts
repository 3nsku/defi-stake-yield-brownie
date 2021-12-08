import {useEthers, useContractFunction} from '@usedapp/core'
import { constants,utils  } from 'ethers'
import { Contract } from "@ethersproject/contracts"
import TokenFarm from "../chain_info/contracts/TokenFarm.json"
import ERC20 from "../chain_info/contracts/MockERC20.json"
import networkMapping from "../chain_info/deployments/map.json"
import {useEffect, useState} from "react"
 
 export const useStakeTokens = (tokenAddress: string) => {
    
   const {chainId} = useEthers() 
   const abi_tokenFarm = TokenFarm.abi //get abi of token farm contract
   const tokenFarmAddress = chainId ? networkMapping[String(chainId)]["TokenFarm"][0] : constants.AddressZero
   const tokenFarmInterface = new utils.Interface(abi_tokenFarm)
   const tokenFarmContract = new Contract(tokenFarmAddress, tokenFarmInterface)

   const erc20_abi = ERC20.abi
   const erc20Interface = new utils.Interface(erc20_abi)
   const erc20Contract = new Contract(tokenAddress, erc20Interface)

   const [amountToStake, setAmountToStake] = useState("0")

    //approve function
   const {send: ApproveErc20Send, state: ApproveErc20State} = useContractFunction(erc20Contract, "approve", { transactionName: 'Approve ERC20 Transfer' })
   
   const ApproveAndStake = (amount: string) => {
      setAmountToStake(amount)
      return ApproveErc20Send(tokenFarmAddress, amount)
   }

   //stake functions
   const {send: StakeSend, state: StakeState} = useContractFunction(tokenFarmContract, "stakeTokens", { transactionName: 'Stake Tokens' })

   // useEffect is a hook that gets called when some variable changes value.
   // you can "track" different variables inside the array at the end 
   useEffect(()=> {
      if(ApproveErc20State.status === "Success") {
         //stake function
         StakeSend(amountToStake, tokenAddress)
         
      }
   }, [ApproveErc20State, amountToStake, tokenAddress])

   const [state, setState] = useState(ApproveErc20State)

   useEffect(() => {
      if (ApproveErc20State.status === "Success") {
         setState(StakeState)
      } else {
         setState(ApproveErc20State)
      }
   }, [ApproveErc20State, StakeState])

   return {ApproveAndStake, state}
 }




